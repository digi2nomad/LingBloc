import unittest

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

if __name__ == '__main__':
    # test(client,"gemini-2.5-flash")
    # list_uploaded_files(client)
    # h, m, s, ms = parse_timestamp_fields("04:23,300")
    # print(calculate_time(h, m, s, ms, 263.62))
    # with open("clips/script-saved-2.txt", "r") as file:
    #    script = file.read()
    #    script = adjust_timestamps(script, 263.62)
    # print(script)
    unittest.main()
