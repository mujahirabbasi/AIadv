import datetime
import numpy as np
import os
import os.path as osp
import glob
import cv2
import insightface
from insightface.app import FaceAnalysis
from insightface.data import get_image as ins_get_image
import matplotlib.pyplot as plt
import moviepy.editor as mp
import moviepy.editor as mpe
import requests
from bs4 import BeautifulSoup
import re
import json
import argparse


def main (args) :
        
        # Scraping images
        def extract_image_urls(url):
            # Send a GET request to the Amazon URL
            response = requests.get(url)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all image containers
                image_containers = soup.find_all('div', class_='imgTagWrapper')

                # Extract image URLs from each container
                image_urls = []
                for container in image_containers:
                    # Find the img tag
                    print (container)
                    img_tag = container.find('img')
                    if img_tag:
                        # Extract the 'data-a-dynamic-image' attribute
                        dynamic_image_data = img_tag.get('data-a-dynamic-image')
                        if dynamic_image_data:
                            # Parse JSON data
                            image_data = json.loads(dynamic_image_data)
                            # Get all image URLs from the dynamic image data
                            for url in image_data.keys():
                                image_urls.append(url)
                        else:
                            print("No dynamic image data found.")
                    else:
                        print("No img tag found in the container.")
                
                return image_urls
            else:
                print("Failed to retrieve the webpage.")
                return None

        def save_image(image_url, filename):
            # Send a GET request to the image URL
            response = requests.get(image_url)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Open a file in binary write mode
                with open(filename, 'wb') as f:
                    # Write the image content to the file
                    f.write(response.content)
                print("Image saved as", filename)
            else:
                print("Failed to download the image.")

        # Amazon URL
        amazon_url = args.u
        # amazon_url = "https://www.amazon.com/Columbia-Powder-Jacket-Black-Large/dp/B07JW4TL96/?th=1"

        # Extract image URLs
        image_urls = extract_image_urls(amazon_url)
        if image_urls:
            # Save each image
            for idx, image_url in enumerate(image_urls):
                # Get the image filename from the URL
                filename = f"jacket_image_{idx + 1}.jpg"
                
                # Save the image
                save_image(image_url, filename)
        else:
            print("Failed to extract the image URLs.")


        # Face detectiona and swapping

        app = FaceAnalysis(name='buffalo_l')
        app.prepare(ctx_id=0, det_size=(640, 640))

        swapper = insightface.model_zoo.get_model('./inswapper_128.onnx',
                                        download=False,
                                        download_zip=False)


        # Loop thorough the frame and swap

        def face_swap(video, output_video, img, app, swapper,
                        plot_before=True, plot_after=True):

            n=0
            cap = cv2.VideoCapture(video)
            img_fn = cv2.imread(img)
            face1 = app.get(img_fn)[0]

            if not cap.isOpened():
                print("Error: Could not open video file.")
                return

            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Define the codec and create VideoWriter object
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(output_video, fourcc, fps, (frame_width, frame_height))


            while cap.isOpened():
                ret, frame = cap.read()
                if ret :
                    face2 = app.get(frame)
                    if face2:
                        frame2_ = swapper.get(frame, face2[0], face1, paste_back=True)
                        n+=1
                        print ("Frame number : ", n)

                if not ret:
                    break

                # Write the frame to the output video
                out.write(frame2_)

            # Release the video capture and video writer objects
            cap.release()
            out.release()

            print("Video saved as", output_video)

        # Path to the input video file

        _ = face_swap(args.v, './face_swap_output_video.mp4', args.i, app, swapper)


        # Extract Audio

        def extract_audio(video_path, output_path):


            # Load the video clip
            clip = mp.VideoFileClip(video_path)

            # Extract the audio from the video clip
            audio = clip.audio

            # Write the audio to a separate file
            audio.write_audiofile(output_path)

            # Release resources used by the clip
            clip.close()

        # Example usage
        video_path = args.v
        output_path = "./extracted_audio.wav"  # You can choose the desired audio format (e.g., mp3)
        extract_audio(video_path, output_path)


        # Integrate Audio and Video

        def combine_audio(vidname, audname, outname, fps=25):

            my_clip = mpe.VideoFileClip(vidname)
            audio_background = mpe.AudioFileClip(audname)
            final_clip = my_clip.set_audio(audio_background)
            final_clip.write_videofile(outname, codec='libx264', fps=fps)


        video_path = "./face_swap_output_video.mp4"
        audio_path = "./extracted_audio.wav"
        output_path = "./integrated_audio_video.mp4"

        combine_audio(video_path, audio_path, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script description here")

    # Add arguments
    parser.add_argument("--u", type=str, help="URL argument")
    parser.add_argument("--v", type=str, help="Video file argument")
    parser.add_argument("--i", type=str, help="Image file argument")

    # Parse arguments
    args = parser.parse_args()

    # Call main function with parsed arguments
    main(args)


