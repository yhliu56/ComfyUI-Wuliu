import re
#import datetime

def time_convert_seconds_to_hmsm(seconds) -> str:
    hours = int(seconds // 3600)
    seconds = seconds % 3600
    minutes = int(seconds // 60)
    milliseconds = int(seconds * 1000) % 1000
    seconds = int(seconds % 60)
    return "{:02d}:{:02d}:{:02d},{:03d}".format(hours, minutes, seconds, milliseconds)


def text_to_srt(idx: int, msg: str, start_time: float, end_time: float) -> str:
    #print(datetime.timedelta(seconds=start_time))
    start_time = time_convert_seconds_to_hmsm(start_time)
    end_time = time_convert_seconds_to_hmsm(end_time)
    srt = """%d
%s --> %s
%s
""" % (
        idx,
        start_time,
        end_time,
        msg,
    )
    return srt


class TranscribeSrt:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "transcribe": ("STRING",),
            },
        }

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("srt", )
    FUNCTION = "transcribe_to_srt"
    CATEGORY = "Wuliu-Srt"

    def transcribe_to_srt(self, transcribe):
        lines = [line.strip() for line in transcribe.split('\n') if line.strip()]
        pattern = r'([0-9]+[.0-9]*)[^0-9]*([0-9]+[.0-9]*)[ )）:：]+([^ )）:：]+.*)'
        res = []
        for i, line in enumerate(lines):
            match = re.findall(pattern, line)
            match = match[0]
            start = match[0]
            end = match[1]
            text = match[2]
            res.append(text_to_srt(i + 1, text, float(start), float(end)))
        res = "\n".join(res) + "\n"

        return (res, )


if __name__ == '__main__':
    srt = TranscribeSrt()
    text = '''
        (0.0, 1.2) 你还是少说几句吧
        (1.2, 2.34) 你放肆
        (2.34, 4.8) 小小人仙竟然敢妄言我西方教教义
    '''
    text = '''
        1.2-2.34: 你放肆
        2.34-4.8: 小小人仙竟然敢妄言我西方教教义
    '''
    print(srt.transcribe_to_srt(text))