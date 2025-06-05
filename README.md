# MBU Export Images from Romexis

This project is a Python-based automation framework designed to export images from the Romexis database and send them via email.


## Process

- **Image Export**: Extracts images from the Romexis database based on patient information.
- **Image Processing**: Adds black bars and text annotations to images.
- **Zips the files**: Compresses processed images into ZIP archives for email delivery.
- **Email Delivery**: Sends zip-archive as email attachments, with support for splitting large ZIP files.
