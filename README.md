# AI-Vision to G-Code: The One-Person Frontier Lab

## Problem & Insight
The primary bottleneck in rapid physical prototyping is the translation layer between human ideation and machine execution. Moving a simple sketch to physical hardware usually requires scanning, converting vectors, importing to CAD, generating toolpaths in CAM, and exporting machine instructions. [cite_start]This project addresses a meaningful prototyping bottleneck by collapsing a multi-hour organizational workflow into a 5-second automated pipeline[cite: 12]. 

By combining local computer vision for precise spatial bounding with a Large Language Model (LLM) acting as a CAM processor, this tool allows users to draw a sketch and instantly compile it into safe, executable G-code for high-speed 2D gantry systems.

## Execution & Technical Architecture
[cite_start]This application is built using a Python/Streamlit frontend and a hybrid local/cloud backend, demonstrating substantial technical integration[cite: 16]:
* **Image Preprocessing (OpenCV):** Uploaded sketches are thresholded to isolate the drawn paths.
* **Fiducial Scaling System:** The system uses `RETR_LIST` contour detection to identify a drawn bounding box (a square surrounding the sketch). It uses this box as a physical reference frame, clamping and scaling all interior coordinate structures to the strict 210x210 mm limits of the hardware. 
* **Data Optimization:** The Ramer-Douglas-Peucker algorithm (`approxPolyDP`) simplifies the extracted paths, reducing memory payload and preventing kinematic buffer overflows.
* **AI CAM Compilation:** The sanitized, floating-point coordinate arrays are passed to an LLM via API. A strictly prompted system prompt formats the arrays into standard G-code, applying safe kinematics limits (`F9000` for rapid travel, `F1500` for linear extrusion).

## Evaluation & Evidence
[cite_start]This system was validated physically on a modified Ultimaker 3 high-speed gantry system to validate claims of machine safety and toolpath efficiency[cite: 21]. 
* **Testing:** Initial physical benchmarks revealed that raw pixel coordinate arrays would crash the machine. Implementing the spatial bounding box successfully constrained the toolhead, completely eliminating the risk of physical endstop collisions.
* **Iteration:** Physical air prints proved that the simplified contour logic provided the smoothest motor translations, allowing the hardware to glide through generated toolpaths at `F9000` without skipping steps.

## Setup & Installation
1. Clone this repository.
2. Install dependencies: `pip install streamlit opencv-python numpy openai`
3. Run the local server: `streamlit run app.py`
4. Upload a sketch (ensure your drawn path is enclosed inside a drawn square to act as the bounding box).
5. Input your API key and compile. 

## Process, Integrity & Disclosure
[cite_start]In accordance with the CS 153 AI Policy, AI tools were utilized to scale development speed[cite: 29].
* **Architecture:** AI was used as a pair programmer to draft the initial Streamlit boilerplate and assist with OpenCV syntax.
* **LLM Integration:** An LLM API (OpenAI GPT-4o) is used dynamically at runtime within the app to format the coordinate payloads into `G0` and `G1` commands based on the injected hardware constraints. 
* **My Contribution:** I focused my engineering effort on system integration, prompt engineering for kinematic constraints, memory handling of the data arrays, and physical hardware validation on the gantry system.
