import streamlit as st
import cv2
import numpy as np
import openai

# Set up the UI layout
st.title("AI-Vision to G-Code Pipeline for High-Speed Gantry Systems")
st.write("Upload a line drawing to extract gantry toolpaths.")

# FIX: Initialize path_payload at the global scope to prevent NameErrors
path_payload = []

# Create a file uploader
uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    # Read the image file as bytes, then convert to an OpenCV format
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
    
    # SAFETY CHECK: Ensure OpenCV successfully decoded the image
    if image is not None:
        st.image(image, caption="1. Original Upload (Grayscale)", use_container_width=True)
        
        # --- PREPROCESSING PIPELINE ---
        
        # 1. Thresholding: Convert to pure black and white (binary)
        _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
        
        # CRITICAL FIX: Changed to RETR_LIST so it sees shapes inside the drawn square
        contours, hierarchy = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        # 1. Identify the Reference Frame (The drawn square)
        largest_area = 0
        reference_box = None
        bx, by, bw, bh = 0, 0, 0, 0
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            if area > largest_area:
                largest_area = area
                reference_box = contour
                bx, by, bw, bh = x, y, w, h

        # 2. Calculate the Scaling Factor
        # Map the drawn square's largest dimension to the 210mm physical bed size
        PHYSICAL_BED_SIZE = 210.0
        # Prevent division by zero if an empty image is somehow uploaded
        scale = PHYSICAL_BED_SIZE / max(bw, bh) if max(bw, bh) > 0 else 1.0
        
        simplified_paths = []
        epsilon_factor = 0.005 
        preview_image = np.zeros_like(image)

        for contour in contours:
            # Skip the bounding box itself so the gantry doesn't try to draw the outer square
            if contour is reference_box:
                continue
                
            epsilon = epsilon_factor * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            if len(approx) > 2: 
                # 3. Translate and Scale Coordinates
                scaled_path = []
                for pt in approx:
                    # Subtract the bounding box X/Y offset to zero the coordinates
                    # Then multiply by the scale factor to map it to real-world millimeters
                    real_x = round((pt[0][0] - bx) * scale, 2)
                    real_y = round((pt[0][1] - by) * scale, 2)
                    
                    # Hardware Safety Clamp: Force numbers strictly between 0 and 210
                    real_x = max(0.0, min(PHYSICAL_BED_SIZE, real_x))
                    real_y = max(0.0, min(PHYSICAL_BED_SIZE, real_y))
                    
                    scaled_path.append((real_x, real_y))
                    
                simplified_paths.append(scaled_path)
                cv2.drawContours(preview_image, [approx], -1, (255, 255, 255), 2)
        
        st.image(preview_image, caption="2. Extracted & Scaled Vector Paths", use_container_width=True)
        st.success(f"Successfully extracted {len(simplified_paths)} scaled paths within 210x210 bounds!")
        
        # Assign the scaled coordinates directly to our payload
        path_payload = simplified_paths
            
        st.write("Data format ready for API routing (Preview of the first 5 nodes of Path 1):")
        if path_payload:
            st.json(path_payload[0][:5]) 
        
    else:
        st.error("Error: OpenCV could not decode the image. Please try a different file.")

st.divider()
st.subheader("3. AI G-Code Compilation")

# API Configuration input field
api_key = st.text_input("Enter API Key (OpenAI or Compatible)", type="password")

if st.button("Generate G-Code via API"):
    if not api_key:
        st.error("Please enter an API key to proceed.")
    elif not path_payload:
        st.error("No valid paths extracted. Please upload an image first.")
    else:
        with st.spinner("Compiling toolpaths via AI..."):
            try:
                # Initialize the OpenAI client
                client = openai.OpenAI(api_key=api_key)
                
                # Format the payload data as a clean string for the LLM context
                data_string = str(path_payload)
                
                # The System Prompt enforces the kinematics rules for your physical gantry
                system_prompt = """
                You are an expert CNC and 3D printing CAM processor. 
                You will receive a list of paths, where each path is a list of (X, Y) coordinates.
                
                Your task is to convert this into standard G-code for a custom high-speed gantry system.
                
                Rules:
                1. Start with a header: Set units to millimeters (G21), absolute positioning (G90).
                2. Set the travel speed for non-extruding moves (G0) to F9000.
                3. Set the extrusion/cutting speed for linear moves (G1) to F1500.
                4. For each path:
                   - G0 to the first coordinate of the path.
                   - G1 to all subsequent coordinates in that path.
                5. Return ONLY the raw G-code text. No markdown formatting, no explanations.
                """
                
                # Make the inference call
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Here are the coordinates to compile: {data_string}"}
                    ],
                    temperature=0.1 # Enforce low temperature to guarantee strict coordinate mapping
                )
                
                # Extract the content and safely check if it is None before stripping
                raw_content = response.choices[0].message.content
                
                if raw_content is None:
                    st.error("The API returned an empty response. Please try clicking generate again.")
                else:
                    gcode_output = raw_content.strip()
                    
                    # Strip out accidental markdown code blocks if present
                    if gcode_output.startswith("```"):
                        gcode_output = "\n".join(gcode_output.split("\n")[1:-1])
                    
                    st.success("G-Code Successfully Compiled!")
                    st.code(gcode_output, language="gcode")
                    
                    # Provide a direct download widget for the generated toolpath artifact
                    st.download_button(
                        label="Download .gcode File",
                        data=gcode_output,
                        file_name="ai_generated_path.gcode",
                        mime="text/plain"
                    )
                
            except Exception as e:
                st.error(f"API Error: {e}")