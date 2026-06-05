# AI-Vision to G-Code: The One-Person Frontier Lab

## Problem & Insight
The primary bottleneck in rapid physical prototyping is the translation layer between human ideation and machine execution. Moving a simple sketch to physical hardware usually requires scanning, converting vectors, importing to CAD, generating toolpaths in CAM, and exporting machine instructions. This project collapses that multi-hour organizational workflow into a 5-second automated pipeline. 

By combining local computer vision for precise spatial bounding with a Large Language Model (LLM) acting as a CAM processor, this tool allows users to draw a sketch and instantly compile it into safe, executable G-code for high-speed gantry systems.

## Execution & Technical Architecture
This application is built using a Python/Streamlit frontend and a hybrid local/cloud backend:
* **Image Preprocessing (OpenCV):** Uploaded sketches are inverted, thresholded, and processed.
* **Skeletonization:** A morphological thinning loop collapses thick 2D ink strokes into 1-pixel wide mathematical center-lines to prevent the hardware from drawing duplicate, overlapping paths.
* **Fiducial Scaling System:** The system uses `RETR_LIST` contour detection to identify a drawn bounding box (a square surrounding the sketch). It uses this box as a physical reference frame, clamping and scaling all interior coordinates to the strict 210x210 mm limits of the hardware.
* **AI CAM Compilation:** The sanitized, floating-point coordinate arrays are passed to an LLM via API. A strictly prompted system prompt formats the arrays into standard G-code, applying safe kinematics limits (`F9000` for rapid travel, `F1500` for linear extrusion) and an auto-home footer.

## Evaluation & Evidence
This system was validated physically on a modified Ultimaker 3 high-speed gantry system. 
* **Failure Analysis:** Initial iterations fed dense pixel arrays to the machine, which overflowed the kinematics buffer and caused severe stuttering. 
* **Solution:** The Ramer-Douglas-Peucker algorithm (`approxPolyDP`) was implemented to dynamically reduce node density while maintaining curve structure, resulting in smooth high-speed physical execution. The fiducial scaling prevents the toolhead from violently crashing into physical endstops.

## Setup & Installation
1. Clone this repository.
2. Install the required dependencies: `pip install streamlit opencv-python numpy openai`
3. Run the local server: `streamlit run app.py`
4. Upload a sketch (ensure your drawn path is enclosed inside a drawn square to act as the bounding box).
5. Input your API key and compile. 

## AI Usage Disclosure
In accordance with the CS 153 AI Policy, AI tools (specifically Gemini) were heavily utilized as a pair programmer to scale development speed.
* **Architecture:** AI was used to draft the initial Streamlit boilerplate and troubleshoot OpenCV morphology syntax (specifically the skeletonization loop and gap-closing functions).
* **LLM Integration:** An LLM API (OpenAI GPT-4o) is used dynamically at runtime within the app to format the coordinate payloads into `G0` and `G1` commands based on the injected hardware constraints. 
* **My Contribution:** I focused my engineering effort on system integration, prompt engineering for kinematic constraints, memory handling of the data arrays, and physical hardware validation/testing.
