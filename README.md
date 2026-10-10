# Instagram API Implementation with Python

## Overview

This project provides a Python script designed to automate the process of publishing images to Instagram using the Facebook Graph API. It integrates with Cloudinary for image hosting  and handles both single image posts and multi-image carousel posts.

### Features

- ✅ Uploads single photos to Cloudinary for external hosting.
- ✅ Uploads multiple photos to Cloudinary.
- ✅ Constructs Graph API endpoints dynamically.
- ✅ Retrieves Instagram Graph API content publishing quotas.
- ✅ Uploads single images to Instagram via the Graph API.
- ✅ Uploads multiple images as carousel items to Instagram.
- ✅ Creates a carousel container for multi-image posts.
- ✅ Publishes single images or carousel containers to Instagram.
- ✅ Orchestrates the entire process from local images to published Instagram posts, handling single vs. carousel based on image count.

### Requirements

    pip install aiohttp
    pip install cloudinary

### Getting Started

    python instagram_api.py
    
The script will:

1. Attempt to load API parameters from a PARAMS.json file. This JSON file must contain your cloudinary_cloud_name, cloudinary_api_key, cloudinary_api_secret, ig_page_id, and ig_access_token.

2. Configure Cloudinary with the provided credentials.

3. Fetch and print your Instagram Graph API content publishing quotas.

4. Automatically posts images from a local folder to Instagram, either as a single picture or a multi-photo carousel.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
