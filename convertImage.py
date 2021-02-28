import json
import tempfile
from findGrid import convert
from boggle import findWords
from google.cloud import storage

# For testing make sure to switch back for prod deployment
storage_client = storage.Client()
# storage_client = storage.Client.from_service_account_json(
#     'tutorialsa.json')


def main(data):
    contentType = data['contentType']
    if contentType == 'application/json':
        print(f"Upload was of type {contentType} so will not be proceeding.")
        return

    fileName = data['name']
    bucketName = data['bucket']
    storageBucket = storage_client.bucket(bucketName)

    blob = storageBucket.get_blob(fileName)
    # blob_uri = f"gs://{bucketName}/{fileName}"

    # _, temp_local_image = tempfile.mkstemp()
    tempImage = tempfile.NamedTemporaryFile(suffix=".png")
    tempImageName = tempImage.name
    tempJSON = tempfile.NamedTemporaryFile(mode="w+", suffix=".json")
    tempJSONName = tempJSON.name

    # Download file from bucket.
    blob.download_to_filename(tempImageName)
    print(f"Image {fileName} was downloaded to {tempImageName}.")

    grid, gridData = convert(tempImageName)
    # if image isnt a spelltower need to do something, maybe here or in findGrid.py
    wordList, wordDict = findWords(tempImageName, grid)

    jsonData = {'positionData': gridData,
                "wordList": wordList, "wordDict": wordDict}

    # Write to temp file HERE
    # json.dump(jsonData, file)
    print("Before json dump")
    json.dump(jsonData, tempJSON)
    print("After json dump")

    i = fileName.index('.')
    name = fileName[:i]
    # finalName = name + '/' + name + '.json'
    finalName = name + '.json'
    newBlob = storageBucket.blob(finalName)
    newBlob.upload_from_filename(tempJSONName)

    print(f"JSON data of image uploaded to: gs://{bucketName}/{finalName}")

    # Close temporary files
    tempImage.close()
    tempJSON.close()


# if __name__ == "__main__":
#     main('newApp/2.jpeg')


# Envelope: {'message': {'attributes': {'bucketId': 'spelltowersolver-305522.appspot.com', 'eventTime': '2021-02-27T01:51:27.526633Z', 'eventType': 'OBJECT_FINALIZE', 'notificationConfig': 'projects/_/buckets/spelltowersolver-305522.appspot.com/notificationConfigs/16', 'objectGeneration': '1614390687433026', 'objectId': 'ColorTower.json', 'payloadFormat': 'JSON_API_V1'},
#                        'data': 'ewogICJraW5kIjogInN0b3JhZ2Ujb2JqZWN0IiwKICAiaWQiOiAic3BlbGx0b3dlcnNvbHZlci0zMDU1MjIuYXBwc3BvdC5jb20vQ29sb3JUb3dlci5qc29uLzE2MTQzOTA2ODc0MzMwMjYiLAogICJzZWxmTGluayI6ICJodHRwczovL3d3dy5nb29nbGVhcGlzLmNvbS9zdG9yYWdlL3YxL2Ivc3BlbGx0b3dlcnNvbHZlci0zMDU1MjIuYXBwc3BvdC5jb20vby9Db2xvclRvd2VyLmpzb24iLAogICJuYW1lIjogIkNvbG9yVG93ZXIuanNvbiIsCiAgImJ1Y2tldCI6ICJzcGVsbHRvd2Vyc29sdmVyLTMwNTUyMi5hcHBzcG90LmNvbSIsCiAgImdlbmVyYXRpb24iOiAiMTYxNDM5MDY4NzQzMzAyNiIsCiAgIm1ldGFnZW5lcmF0aW9uIjogIjEiLAogICJjb250ZW50VHlwZSI6ICJhcHBsaWNhdGlvbi9vY3RldC1zdHJlYW0iLAogICJ0aW1lQ3JlYXRlZCI6ICIyMDIxLTAyLTI3VDAxOjUxOjI3LjUyNloiLAogICJ1cGRhdGVkIjogIjIwMjEtMDItMjdUMDE6NTE6MjcuNTI2WiIsCiAgInN0b3JhZ2VDbGFzcyI6ICJTVEFOREFSRCIsCiAgInRpbWVTdG9yYWdlQ2xhc3NVcGRhdGVkIjogIjIwMjEtMDItMjdUMDE6NTE6MjcuNTI2WiIsCiAgInNpemUiOiAiMzI3NzQiLAogICJtZDVIYXNoIjogImZ6dUxJZi9ZWXZhN2ErKy84Q2p6Tmc9PSIsCiAgIm1lZGlhTGluayI6ICJodHRwczovL3d3dy5nb29nbGVhcGlzLmNvbS9kb3dubG9hZC9zdG9yYWdlL3YxL2Ivc3BlbGx0b3dlcnNvbHZlci0zMDU1MjIuYXBwc3BvdC5jb20vby9Db2xvclRvd2VyLmpzb24/Z2VuZXJhdGlvbj0xNjE0MzkwNjg3NDMzMDI2JmFsdD1tZWRpYSIsCiAgImNyYzMyYyI6ICJYS1gzZlE9PSIsCiAgImV0YWciOiAiQ01LQzBQdjVpTzhDRUFFPSIKfQo=', 'messageId': '2071743114691569', 'message_id': '2071743114691569', 'publishTime': '2021-02-27T01:51:27.777Z', 'publish_time': '2021-02-27T01:51:27.777Z'}, 'subscription': 'projects/spelltowersolver-305522/subscriptions/imageUploadSubscription'}
