import unittest

from util.srt_utils import divide_subtitles


class MyTestCase(unittest.TestCase):
    def test_something(self):
        sub_chunks = divide_subtitles("clips/script.txt", 100)
        for i, chunk in enumerate(sub_chunks):
            save_file = "clips/script_chunk_" + str(i) + ".txt"
            with open(save_file, "w", encoding="utf-8") as file:
                file.write(chunk)


if __name__ == '__main__':
    unittest.main()
