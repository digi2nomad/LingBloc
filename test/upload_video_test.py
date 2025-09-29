import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        # upload_video(cred,
        #             "clips/English.mp4",
        #             "Test Video from API",
        #             "This is a test video uploaded via YouTube API",
        #             "clips/thumbnail-english.jpg")
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
