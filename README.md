# pits (python image-to-speech)

![pitsy, the pits pit python](https://raw.github.com/alexnbenjamin/pits/master/pits.png)

This is Pitsy, the pits pit python.

##### Overview
Pits provides users the ability to generate accurate synthesized speech translations of important text within images. Users submit an image containing a document or sign, and pits detects the region of interest, warps the text perspective to normal, and performs several optimizations before recognizing text and outputting speech.

I developed pits with 3 primary use-cases in mind: assisting the visually impaired reading important documents or signs, helping children learning to read (or users learning a new language), and quickly generating audiobooks and audio-files for listening on the go. It’s developed as an engine, but with those future applications in mind.

##### Usage
Pits is designed as a command-line application with the following usage:
```
python pits.py <your_file_name>
```
You might consider experimenting with the adaptive thresholding parameters (step 3, line 2) to improve your translation. There's also the rate of speech (step 4.2, line 2) to adjust. Last but not least, feel free to edit any of the marked cv2.imwrite commands if you'd prefer not to save intermediate computational artifacts.
