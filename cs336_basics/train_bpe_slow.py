import regex as re
import time

def train_bpe(
    input_path: str, 
    vocab_size: int,
    special_tokens: list[str]
):

    ### read text from input_path
    with open(input_path, 'r') as file:
        text = file.read()


    ### initialize vocabulary
    vocab = {i: x.encode("utf-8") for i, x in enumerate(special_tokens)}
    vocab.update({i+len(special_tokens): bytes([i]) for i in range(256)})
    len_vocab = len(vocab)
    print("Initial vocabulary size", len_vocab)


    ### pre tokenization
    # splits = text.replace("\n", " ").split(" ")
    PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
    freq = {}
    text_splits = re.split("|".join(special_tokens), text)
    for text_i in text_splits:
        # if text_i == "|":
        #     continue
        for s in re.finditer(PAT, text_i):
            s = s.group(0)
            s = tuple([bytes([i]) for i in s.encode("utf-8")])
            freq[s] = freq.get(s, 0) + 1
    # print(freq)


    ### merge
    merges = []

    while len_vocab < vocab_size:

        ### count frequency of every successive pair of bytes
        cnt_bytes_pairs = {}
        appear_bytes_pairs = {}
        for s in freq:
            if len(s) == 1:
                continue # nothing to merge
            bytes_pair_to_index = {}
            for j in range(len(s)-1):
                bytes_pair = (s[j], s[j+1])
                bytes_pair_to_index[bytes_pair] = bytes_pair_to_index.get(bytes_pair, []) + [j]
            for bytes_pair in bytes_pair_to_index:
                cnt_bytes_pairs[bytes_pair] = cnt_bytes_pairs.get(bytes_pair, 0) + freq[s]*len(bytes_pair_to_index[bytes_pair])
                appear_bytes_pairs[bytes_pair] = appear_bytes_pairs.get(bytes_pair, []) + [(s, bytes_pair_to_index[bytes_pair])]
            
        
        if len(cnt_bytes_pairs) == 0:
            break
        
        # print(cnt_bytes_pairs)
        # print(appear_bytes_pairs)

        ### find the pair with largest frequency
        merged_pair = merged_pair = max(cnt_bytes_pairs, key=lambda k: (cnt_bytes_pairs[k], k))
        merges.append(merged_pair)
        vocab[len_vocab] = merged_pair[0]+merged_pair[1]
        len_vocab += 1
        # print("Merge", merged_pair)

        ### update word-freq dict
        bytes_to_be_merged = appear_bytes_pairs[merged_pair]
        # bytes_to_be_merged_dict = {}
        # for s, j in bytes_to_be_merged:
        #     if s in bytes_to_be_merged_dict:
        #         bytes_to_be_merged_dict[s].append(j)
        #     else:
        #         bytes_to_be_merged_dict[s] = [j]

        # print(bytes_to_be_merged_dict)
        for s, indices in bytes_to_be_merged:
            s_new = s[:indices[0]] + tuple([s[indices[0]]+s[indices[0]+1]])
            for k in range(1, len(indices)):
                s_new += s[indices[k-1]+2:indices[k]]
                s_new += tuple([s[indices[k]]+s[indices[k]+1]])
            s_new += s[indices[-1]+2:]
            freq[s_new] = freq.get(s_new, 0) + freq[s]
            # print(s, s_new)
            del freq[s]
        # print(freq)

    print("Final vocabulary size", len_vocab)
    return vocab, merges



if __name__ == "__main__":

    input_path = "/home/ec2-user/assignment1-basics/tests/fixtures/corpus.en"
    # "/home/ec2-user/data/simple_text.txt"
    vocab_size = 500
    special_tokens = ["<|endoftext|>"]

    start = time.time()
    vocab, merges = train_bpe(input_path, vocab_size, special_tokens)
    end = time.time()

    print(merges)
    print(vocab)
    print(end-start)
