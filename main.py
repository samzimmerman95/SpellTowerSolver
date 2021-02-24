import json
from findGrid import convert
from boggle import findWords
from google.cloud import storage


def hello_gcs(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    print(f"Processing file: {event['name']}.")
    print("event:", event)
    print("context: ", context)

    contentType = event['contentType']
    if contentType == 'application/json':
        pass
    else:
        main(event['name'])

    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

#     storage_client = storage.Client()
#     bucket = storage_client.bucket(event['bucket'])
#     blob = bucket.blob("testbob.txt")

#     blob.upload_from_filename("test.txt")


def main(fileName):
    grid, data = convert(fileName)
    wordList, wordDict = findWords(fileName, grid)

    jsonData = {'positionData': data,
                "wordList": wordList, "wordDict": wordDict}
    file = open('output.json', 'w')
    json.dump(jsonData, file)

    i = fileName.index('/')
    name = fileName[:i]
    storage_client = storage.Client()
    bucket = storage_client.bucket('spelltowersolver-305522.appspot.com')
    blob = bucket.blob(name + '/' + name + '.json')

    blob.upload_from_filename("output.json")


# if __name__ == "__main__":
#     main('newApp/2.jpeg')
