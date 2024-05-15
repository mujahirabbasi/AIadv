# AI meets Advertisement

## Overview

This project consists of multiple functionalities integrated into a single script:
1. Scraping jacket images from a URL.
2. Performing face swapping between a person in an image and video.
3. Conducting jacket swapping between downloaded jacket images and the same video.
4. Adding audio into the final video extracted from the same video.

## Requirements

- Python 3.x
- pip install -r requirements.txt
- The pretarined weights for face swapping can be downloaded from here : https://www.reddit.com/r/midjourney/comments/13pnraj/please_reupload_inswapper_128onnx/


## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mujahirabbasi/AIadv.git


## Usage

python custom_video_gen.py --u "https://www.amazon.com/Columbia-Powder-Jacket-Black-Large/dp/B07JW4TL96/?th=1" --v "./jacket.mp4" --i "./generated_model.jpg"
