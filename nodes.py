import re
import jieba
#import datetime

def split_by_token(text, max_len=256):
    """ 按切词切割拼装成不大于 max_len 的 短文本list

    Args:
        text: 文本
        max_len: 短文本最大长度

    Returns:
        短文本 list
    """

    tokens = jieba.cut(text)
    splits = []
    split = ""
    for sent in tokens:
        if len(split + sent) > max_len:
            splits.append(split)
            split = sent
        else:
            split += sent
    if split != "":
        splits.append(split)

    return splits


def split_by_word(sentence, max_sent_len=256):
    """ 句子分隔

    Args:
        sentence: 长句子文本
        max_sent_len: 句子最大长度

    Returns:
        句子list
    """

    # 短句子分隔符
    sentence_delimiters = ['. ']
    sentences = [sentence]
    for sep in sentence_delimiters:
        split_sents = []
        for sent in sentences:
            _splits = sent.split(sep)
            for _s in _splits[:-1]:
                split_sents.append(_s + sep)
            split_sents.append(_splits[-1])
        sentences = split_sents

    result = []
    for sent in sentences:
        if len(sent) >  max_sent_len:
            # 先按空格切
            _splits = sent.split(' ')
            _len = len(_splits)
            for _i, _s in enumerate(_splits):
                if _i < _len - 1:
                    # 空格为原文本字符
                    _s = _s + ' '
                if len(_s) > max_sent_len:
                    result.extend(split_by_token(_s, max_sent_len))
                else:
                    result.append(_s)

        else:
            result.append(sent)

    return result


def split_sentences(content, max_sent_len=128):
    """ 句子分隔

    Args:
        content: 文本内容
        max_sent_len: 句子最大长度

    Returns:
        句子list
    """

    if not content:
        return ['']

    sentence_delimiters = set(['?', '!', ';', '？', '！', '。', '；', '……', '…', '\n'])
    sentences = []
    sentence = ""
    for word in content:
        sentence += word
        if word in sentence_delimiters:
            if len(sentence) > max_sent_len:
                sentences.extend(split_by_word(sentence, max_sent_len))
            else:
                sentences.append(sentence)
            sentence = ""

    if sentence != "":
        if len(sentence) > max_sent_len:
            sentences.extend(split_by_word(sentence, max_sent_len))
        else:
            sentences.append(sentence)

    return sentences


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

    def transcribe_to_srt(self, transcribe, text=None):
        lines = [line.strip() for line in transcribe.split('\n') if line.strip()]
        pattern = r'([0-9]+[.0-9]*)[^0-9]*([0-9]+[.0-9]*)[ )）:：]+([^ )）:：]+.*)'

        res = []
        for i, line in enumerate(lines):
            match = re.findall(pattern, line)
            match = match[0]
            start = match[0]
            end = match[1]
            s = match[2]
            if text is None:
                res.append(text_to_srt(i + 1, s, float(start), float(end)))
            else:
                res.append((float(start), float(end), s))

        if text is None:
            res = "\n".join(res) + "\n"
            return (res, )
        
        sentences = split_sentences(text, max_sent_len=128)
        time_stamps = res
        start = 0
        time_stamps_len = len(time_stamps)
        res = []
        for i, sent in enumerate(sentences):
            s = sent.strip()
            start_time = time_stamps[start][0]
            while start < time_stamps_len:
                i = s.find(time_stamps[start][2])
                if i < 0:
                    break
                s = s[i+1:]
                start += 1
            if start >= time_stamps_len:
                start -= 1
            end_time = time_stamps[start][1]
            res.append(text_to_srt(i + 1, sent, start_time, end_time))

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

    text = '真的美，千红百媚，偏偏只为你而醉。'
    time_stamps = '''
        0.00-0.16: 真
        1.44-1.52: 的
        1.52-1.60: 美
        1.60-1.76: 千
        2.00-2.08: 红
        2.16-2.24: 百
        2.48-2.48: 媚
        2.64-2.72: 偏
        2.72-2.72: 偏
        3.36-3.44: 只
        3.52-3.52: 为
        3.52-3.52: 你
        3.52-3.52: 而
        4.96-4.96: 醉
    '''
    print(srt.transcribe_to_srt(time_stamps, text))