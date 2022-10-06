# City Story

A project by [Studio Dott](https://studiodott.be) which brings frictionless tagging of media fragments residing on a public Google Drive folder.

It can easily be deployed to [Heroku](https://heroku.com) and stores its processed media files on any S3-compatible object store, such as [Wasabi](https://wasabi.com) or [Amazon](https://aws.amazon.com/s3/).

## Requirements

This application uses external services where it can discover and later store media files. Here we'll give some pointers on how to set those up.

### Google Drive

The application searches for new media files on a given Google Drive folder. We'll need some details about both the folder and the identity it'll assume to talk to it.

#### Folder

Any publically viewable folder can be used. You can select a folder, edit its sharing details and select "Anyone with the link" under "General access", and finally "Copy link".

In this copied link is the identity of the folder we need. The link will have the format `https://drive.google.com/drive/folders/LONGRANDOMWORD?usp=sharing`, please save the "LONGRANDOMWORD" in there, this is the folder's identity.

#### API key

When reading a Google Drive folder, City Story needs to tell Google under which person's name this transaction will happen. This is done by providing an API key.

Please go to the [Google Cloud Console](https://console.cloud.google.com) and log in with your Google account, doing any needed setup work to get there. Then, in the menu, head over to "APIs & Services", and open "Credentials". At that page, press the "+ create credentials" button up top, and select "API key". A pop-up will tell you your API key, which will be a very random-looking bunch of characters, please note it down.

### S3

S3 is a type of object storage (in which files can be stored and retrieved on "buckets" via HTTP). It was cooked up by Amazon but by now multiple vendors offer this using a uniform interface. City Story has been tested with both Amazon and Wasabi, but any S3-compatible vendor you prefer should fit right in there. As an example, we will be using Wasabi in this document.

#### General setup

Any vendor you choose will require you to create an account, so you'll need to do that first. For Wasabi, please head over to their [signup page](https://wasabi.com/sign-up) and take it from there.

#### Bucket setup

On the console page of your chosen S3 provider, find the button to create a new "bucket". A bucket will hold all of your files, reachable at it's URL. You'll need to give it a name, and probably need to choose a "region", which is the geographical region on your files will physically reside. At this step, we need to note down both the bucket name we choose, and the URL it will end up on (depending on the region).

(On Wasabi, specifically the [console](https://console.wasabisys.com/) we press the "Create Bucket" button, and fill in the name we made up for it and set it's region. In this example, the name is "citystory-demo-bucket" and the region is "Amsterdam eu-central-1". We see the bucket will end up on "s3.eu-central-1.wasabisys.com", and make note of that. We can just create the bucket here, no other actions needed.)

Then we head on over to the bucket's settings, and find a place where we can tell this S3 provider that all files on this bucket can be read by anyone (they still will need to know which files, of course). This is usually (and regrettably) configured by uploading a bit of code-ish-looking text in a format called JSON. It will likely be filed under "permissions" or "policy" or somesuch.

(On Wasabi, looking at your list of buckets, open its settings by clicking the three-dots next to it. Head over to "Policies", and paste the following JSON code in there.)

The JSON to use as a policy can be this one (and please replace "YOURBUCKETNAME" by your bucket's name):

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowPublicRead",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::YOURBUCKETNAME/*"
    }
  ]
}
```

(For our example, we replace "YOURBUCKETNAME" with "citystory-demo-bucket".)

#### Key set up

Here too we need to have an API key which we'll use to access this bucket. Anyone can read, but only parties who know the API key may upload files to this bucket. In S3, this is split into two parts, both of which we need to note down. There is the "Access Key ID" and the "Secret Access Key".

(On the Wasabi console, we choose "Access Keys" and hit the "create new access key" button. Select "Root-user" and press "create". In this dialog we find both the Access Key and Secret Key, and we note these down.)

(On Amazon, things are less transparent, it requires creating a user by going to the IAM portal, select the list of users under "Access management" on the left, and pressing the "Add users" button. We give this user a name and select "Access key - Programmatic access". On the next tab, we state what this user should be able to do, selecting "Attach existing policies directly" and enabling "AmazonS3FullAccess". Thankfully all the rest can stay as it is. Finally, after creating this user, we can see their "Access key ID" and "Secret access key", which are the values we need. So easy! Did you know this company is involved in spaceflight?)

### Wrap up

If all went well, we're armed with a few pieces of information:

* The Google Drive folder ID,
* the Google Drive API key,
* the S3 bucket name,
* the S3 endpoint URL,
* the S3 access key ID,
* the S3 secret access key.

We can now install and configure City Story.

## Installation

### Deploying

You can install City Story by pressing this button:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Studiodott/citystory)

If you don't have an account with Heroku, you can create one during this process.

### Configuration

During deployment, you specified the name for your instance of City Story, and it told you the link to access it (most likely in the form of `https://your-instance-name.herokuapp.com`). Head on over there.

You will be asked to log in with an email address (the system will not send you emails). Remember which one you fill in! Because the first user which is created is also the administrator of this instance.

Head on over to the admin tab, to configure this instance. Fill in the values we collected above, and press "Save". You can do a manual sync from Google Drive with the "Manual sync" button. Upon any errors, it will tell you what's going on pretty quickly. If it takes a long while, it is likely doing its job of downloading/processing/uploading media files one by one.

## License

City Story is Open Source, under the [MIT](https://opensource.org/licenses/MIT) licence.
