import streamlit as st
import cv2
import numpy as np

# Set up the UI layout
st.title("AI-Vision to G-Code 🤖")
st.write("Upload a line drawing to generate a gantry path.")

# Create a file uploader
uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    # Read the image file as bytes, then convert to an OpenCV format
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
    
    # SAFETY CHECK: Ensure OpenCV successfully decoded the image
    if image is not None:
        # Display the image in the UI
        st.image(image, caption="Uploaded Image (Grayscale)", use_container_width=True)
        st.success("Image successfully loaded into OpenCV! Ready for path extraction.")
    else:
        # Show an error in the UI if it fails
        st.error("Error: OpenCV could not decode the image. Please try a different file.")
