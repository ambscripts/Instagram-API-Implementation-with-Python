import aiohttp, asyncio, os, json # Imports necessary libraries: aiohttp for asynchronous HTTP requests,
#asyncio for managing async operations, os for operating system interactions, and json for handling JSON data.

#pip install cloudinary
import cloudinary # Imports the Cloudinary SDK for image hosting.
import cloudinary.uploader # Imports Cloudinary's uploader module for uploading files.


def path(folder='', file=''):
    """
    Constructs a file path compatible with different operating systems.
    It returns a path relative to the current working directory.
    :param folder: The name of the subfolder (optional).
    :param file: The name of the file (optional).
    :return: A string representing the constructed file path.
    """
    # os.getcwd() gets the current working directory.
    # .replace(os.sep, '/') ensures forward slashes for consistency, regardless of OS.
    # The slicing '[:len(folder)]' and '[:len(file)]' adds '/' only if folder/file names are provided.
    return os.getcwd().replace(os.sep,'/')+'/'[:len(folder)]+folder+'/'[:len(file)]+file


def get_list(folder, file_name):
    """
    Loads data from a JSON file.
    :param folder: The folder where the JSON file is located.
    :param file_name: The name of the JSON file (without extension).
    :return: The deserialized JSON data, or None if an error occurs.
    """
    try:
        # Opens and loads the JSON file using the path function to construct the full path.
        return json.load(open(path(folder, file_name+".json")))
    except Exception as e:
        print(e) # Prints any exception that occurs during file reading or JSON parsing.
        return None


#UPLOAD SINGLE PHOTO TO CLOUDINARY
async def upload_photo(source):
    """
    Uploads a single photo to Cloudinary.
    :param source: The file path of the image to upload.
    :return: The secure URL of the uploaded image on Cloudinary.
    """
    print("Uploading", source, "...")
    # Uploads the image to Cloudinary, using the file name (without extension) as the public ID.
    result = cloudinary.uploader.upload(source, public_id = source.split('/')[-1].split(".")[0], overwrite = True)
    await asyncio.sleep(0.5) # Asynchronously pauses for 0.5 seconds, good practice for API calls to avoid rate limits.
    return result['secure_url'] # Returns the HTTPS URL of the uploaded image.


#UPLOAD MULTIPLE PHOTOS TO CLOUDINARY
async def host_images(files):
    """
    Uploads multiple photos to Cloudinary concurrently.
    :param files: A list of file paths of the images to upload.
    :return: A list of secure URLs for the uploaded images.
    """
    # Uses a list comprehension with await to upload each photo sequentially and collect their URLs.
    return [await upload_photo(files[i]) for i in range(len(files))]


#BUILD GRAPH API ENDPOINT
def get_endpoint_url(endpoint, user_id):
    """
    Constructs the Facebook Graph API endpoint URL for a given endpoint and user ID.
    :param endpoint: The specific Graph API endpoint (e.g., "media", "content_publishing_limit").
    :param user_id: The Instagram Business Account or Creator Account ID.
    :return: The formatted API endpoint URL.
    """
    # Formats the base Graph API URL with the user_id and specific endpoint.
    return ('https://graph.facebook.com/v21.0/{}/'+endpoint).format(user_id)


#GRAPH API QUOTA
async def get_quotas(user_id, token):
    """
    Retrieves the content publishing quota for an Instagram account.
    :param user_id: The Instagram Business Account or Creator Account ID.
    :param token: The Instagram access token.
    """
    try:
        async with aiohttp.ClientSession() as session: # Creates an aiohttp client session.
            # Makes an asynchronous GET request to the content_publishing_limit endpoint.
            async with session.get(get_endpoint_url("content_publishing_limit", user_id), params={'fields': "config,quota_usage",'access_token': token}) as response:
                results = await response.json() # Parses the JSON response.
                # Prints the current quota usage, total quota, and duration.
                print("quota_usage: ", results['data'][0]['quota_usage'], " - quota_total: ", results['data'][0]['config']['quota_total'], " - quota_duration: ", results['data'][0]['config']['quota_duration'], '\n', sep='')
    except Exception as e:
        print(e) # Prints any exception that occurs during the API call.


#UPLOAD SINGLE IMAGE TO INSTAGRAM
async def upload_single_image_ig(url, caption, user_id, token):
    """
    Uploads a single image to Instagram via the Graph API.
    This creates a media object that can then be published.
    :param url: The URL of the image hosted externally (e.g., Cloudinary).
    :param caption: The caption for the Instagram post.
    :param user_id: The Instagram Business Account or Creator Account ID.
    :param token: The Instagram access token.
    :return: The ID of the created media object if successful, otherwise None.
    """
    try:
        async with aiohttp.ClientSession() as session:
            # Makes an asynchronous POST request to the 'media' endpoint to upload the image.
            async with session.post(get_endpoint_url("media", user_id), data={'image_url': url, 'caption': caption, 'access_token': token}) as response:
                results = await response.json() # Parses the JSON response.
                if( 'id' in results ):
                    print("Image Uploaded To IG Successfully! Id:", results['id'], "Caption:", '"'+caption+'"')
                    return results['id'] # Returns the media ID if the upload was successful.
                else:
                    print("Image Uploading Error!") # Prints an error if 'id' is not in the response.
                    print(results) # Print the full error response for debugging.
    except Exception as e:
        print(e) # Prints any exception that occurs during the API call.


#UPLOAD MULTIPLE IMAGES TO INSTAGRAM
async def upload_multiple_images_ig(url_list, user_id, token):
    """
    Uploads multiple images as carousel items to Instagram via the Graph API.
    Each image is uploaded individually to get its media ID.
    :param url_list: A list of URLs for the images hosted externally.
    :param user_id: The Instagram Business Account or Creator Account ID.
    :param token: The Instagram access token.
    :return: A list of media IDs for the uploaded carousel items.
    """
    try:
        async with aiohttp.ClientSession() as session:
            id_list = [] # Initializes a list to store media IDs.
            for item in url_list: # Iterates through each image URL.
                # Makes a POST request for each image, marking it as a carousel item.
                async with session.post(get_endpoint_url("media", user_id), data={'image_url': item, 'is_carousel_item': "true", 'access_token': token}) as response:
                    results = await response.json()
                    if( 'id' in results ):
                        id_list.append(results['id']) # Adds the media ID to the list.
                        print("Image Uploaded To IG Successfully! Id:", results['id'])
                        await asyncio.sleep(0.5) # Short pause between uploads to respect API limits.
                    else:
                        print("Image Uploading Error!")
                        print(results) # Print the full error response for debugging.
            return id_list # Returns the list of media IDs.
    except Exception as e:
        print(e) # Prints any exception that occurs.


#CREATE CONTAINER FOR CAROUSEL POST
async def create_images_container(id_list, caption, user_id, token):
    """
    Creates a carousel container media object on Instagram using a list of media IDs.
    This container can then be published as a carousel post.
    :param id_list: A list of media IDs for the individual carousel items.
    :param caption: The caption for the carousel post.
    :param user_id: The Instagram Business Account or Creator Account ID.
    :param token: The Instagram access token.
    :return: The ID of the created carousel container if successful, otherwise None.
    """
    try:
        async with aiohttp.ClientSession() as session:
            # Makes a POST request to the 'media' endpoint with media_type CAROUSEL and child IDs.
            async with session.post(get_endpoint_url("media", user_id), data={'caption': caption, 'media_type': "CAROUSEL", 'children': ','.join(id_list), 'access_token': token}) as response:
                results = await response.json()
                if( 'id' in results ):
                    print("Carousel Created Successfully! Id:", results['id'], "Caption:", '"'+caption+'"', "Items count:", len(id_list))
                    return results['id'] # Returns the container ID.
                else:
                    print("Carousel Creation Error!")
                    print(results) # Print the full error response for debugging.
    except Exception as e:
        print(e) # Prints any exception that occurs.


#PUBLISH SINGLE IMAGE OR CONTAINER
async def publish_to_ig(id_, user_id, token):
    """
    Publishes a media object (single image or carousel container) to Instagram.
    :param id_: The ID of the media object (image or carousel container) to publish.
    :param user_id: The Instagram Business Account or Creator Account ID.
    :param token: The Instagram access token.
    :return: The ID of the published post if successful, otherwise None.
    """
    try:
        async with aiohttp.ClientSession() as session:
            # Makes a POST request to the 'media_publish' endpoint to finalize the post.
            async with session.post(get_endpoint_url("media_publish", user_id), data={'creation_id': id_, 'access_token': token}) as response:
                results = await response.json()
                if( 'id' in results ):
                    print("Post Published To IG Successfully! Id:", results['id'])
                    return results['id'] # Returns the published post ID.
                else:
                    print("Post Publishing Error!")
                    print(results) # Print the full error response for debugging.
    except Exception as e:
        print(e) # Prints any exception that occurs.


#HOST IMAGES THEN PUBLISH TO IG (CAROUSEL OR SINGLE IMAGE DEPENDING ON IMAGE COUNT IN FOLDER...)
async def publish_content_to_ig(images_folder, caption, user_id, token):
    """
    Orchestrates the entire process of hosting images and publishing them to Instagram.
    It handles both single image posts and carousel posts based on the number of images.
    :param images_folder: The local folder path containing the images to be published.
    :param caption: The caption for the Instagram post.
    :param user_id: The Instagram Business Account or Creator Account ID.
    :param token: The Instagram access token.
    """
    # Gets a list of full paths for all image files in the specified folder.
    images = [path(images_folder,x) for x in os.listdir(images_folder)]
    images_url = await host_images(images) # Uploads all images to Cloudinary and gets their URLs.

    if( len(images_url) == 1 ):
        # If there's only one image, upload it as a single image post.
        image_id = await upload_single_image_ig(images_url[0], caption, user_id, token)
        if image_id: # Only attempt to publish if image_id was successfully obtained
            await publish_to_ig(image_id, user_id, token)
    elif( len(images_url) > 1 ):
        # If there are multiple images, upload them as carousel items, create a container, then publish.
        images_id_list = await upload_multiple_images_ig(images_url, user_id, token)
        if images_id_list: # Only attempt to create container if image_id_list was successfully obtained
            container_id = await create_images_container(images_id_list, caption, user_id, token)
            if container_id: # Only attempt to publish if container_id was successfully obtained
                await publish_to_ig(container_id, user_id, token)


if __name__ == "__main__":
    # This block demonstrates how to use the Instagram API functions.
    # To run this, you need a 'PARAMS.json' file in your 'Desktop' folder
    # with 'cloudinary_cloud_name', 'cloudinary_api_key', 'cloudinary_api_secret',
    # 'ig_page_id', and 'ig_access_token'.
    # You also need an 'images' folder in your 'Desktop' folder containing images.

    # get params json:
    params = get_list('Desktop','PARAMS')
    if params: # Check if params were loaded successfully
        # set-up cloudinary:
        cloudinary.config(cloud_name=params['cloudinary_cloud_name'], api_key=params['cloudinary_api_key'], api_secret=params['cloudinary_api_secret'])
        
        # quota:
        # Uncomment the line below to get the content publishing quota.
        # await get_quotas(params['ig_page_id'], params['ig_access_token'])

        # publish images to instagram:
        # Uncomment the line below to publish images from 'Desktop/images' folder.
        await publish_content_to_ig('Desktop/images', 'CAPTION TEST', params['ig_page_id'], params['ig_access_token'])
    else:
        print("Failed to load PARAMS.json. Please ensure it exists and is correctly formatted.")