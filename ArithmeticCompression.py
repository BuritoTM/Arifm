class ArithmeticCoder:
    BREAK_SYMBOL = '\0'
    EOF_SYMBOL = '†'

    HIGH = 65536
    HALF = 32768
    QUARTER = 16384
    THIRD_QUARTER = 49152

    def __init__(self, source_text):
        self.source_text = source_text
        self.alphabet = self.get_alphabet()
        self.frequency = self.get_frequency()

    def print_table(self):
        for char, freq in zip(self.alphabet, self.frequency):

            if freq == 538:
                print(
                    f"Специальный символ: {repr(char)} - {char.encode('unicode_escape')}")
                print(f"ASCII код: {ord(char)}")


            if char == '\n':
                display_char = "\\n"
            else:
                display_char = char

            print(f"{display_char} - {freq}")

    def get_alphabet(self):
        alphabet = [self.EOF_SYMBOL]
        for c in self.source_text:
            if c not in alphabet:
                alphabet.append(c)
        return alphabet

    def get_frequency(self):
        freq = [0] * len(self.alphabet)
        for c in self.source_text:
            index = self.alphabet.index(c)
            freq[index] += 1
        for i in range(1, len(freq)):
            freq[i] += freq[i - 1]
        return freq

    def get_symbol_in_alpha(self, symbol):
        if symbol not in self.alphabet:
            print("Символ не найден в алфавите!")
            exit(1)
        return self.alphabet.index(symbol)

    def bits_to_add(self, output, bit, bits_to_add):
        output.append(str(bit))
        output.extend(['1' if not bit else '0'] * bits_to_add)

    def arithmetic_encoding(self):
        encode = []
        text_len = len(self.source_text)

        high = self.HIGH - 1
        low = 0
        del_ = self.frequency[-1]
        print(self.frequency)

        bits_to_add = 0
        i = 0

        while i < text_len:
            current = self.get_symbol_in_alpha(self.source_text[i])
            i += 1

            range_ = high - low + 1
            high = low + (range_ * self.frequency[current]) // del_ - 1
            low = low + (range_ * self.frequency[current - 1]) // del_

            while True:
                if high < self.HALF:
                    self.bits_to_add(encode, 0, bits_to_add)
                    bits_to_add = 0
                elif low >= self.HALF:
                    self.bits_to_add(encode, 1, bits_to_add)
                    bits_to_add = 0
                    low -= self.HALF
                    high -= self.HALF
                elif low >= self.QUARTER and high < self.THIRD_QUARTER:
                    bits_to_add += 1
                    low -= self.QUARTER
                    high -= self.QUARTER
                else:
                    break
                low = 2 * low
                high = 2 * high + 1

        return ''.join(encode)

    def read_16bit(self, encode, current_bit_list):
        value = 0
        bits_in_encode = len(encode)
        for i in range(15, -1, -1):
            if i < bits_in_encode:
                if encode[i] == '1':
                    value |= (1 << current_bit_list[0])
                current_bit_list[0] += 1
        return value


    def add_bit(self, encode, value, current_bit, flag):
        if flag:
            value &= ~1
        elif current_bit >= len(encode):
            value |= 1
            flag = True
        elif encode[current_bit] == '1':
            value |= 1
        elif encode[current_bit] == '0':
            value &= ~1
        return value, flag

    def arithmetic_decoding(self, encode):
        decode = ""
        low = 0
        high = self.HIGH - 1
        del_ = self.frequency[-1]
        current_bit = [0]
        value = self.read_16bit(encode, current_bit)
        not_read = 16 - current_bit[0]
        for _ in range(not_read):
            value *= 2
        flag = False
        while len(decode)< (del_-1):
            range_ = high - low + 1
            frequency = (((value - low) + 1) * del_ - 1) // range_

            symbol_index = 1
            while symbol_index < len(self.frequency) and self.frequency[symbol_index] <= frequency:
                symbol_index += 1

            high = low + (range_ * self.frequency[symbol_index]) // del_ - 1
            low = low + (range_ * self.frequency[symbol_index - 1]) // del_

            decode += self.alphabet[symbol_index]

            if self.alphabet[symbol_index] == self.BREAK_SYMBOL:
                print("Декодирование завершено. Результат:", decode)
                return decode


            while True:
                if high < self.HALF:
                    pass
                elif low >= self.HALF:
                    low -= self.HALF
                    high -= self.HALF
                    value -= self.HALF
                elif low >= self.QUARTER and high < self.THIRD_QUARTER:
                    low -= self.QUARTER
                    high -= self.QUARTER
                    value -= self.QUARTER
                else:
                    break

                low *= 2
                high = 2 * high + 1

                value, flag = self.add_bit(encode, 2 * value, current_bit[0], flag)
                current_bit[0] += 1

        return decode

def write_to_binary_file(encoded_text, frequency_list, alphabet, filename):
    byte_array = bytearray()
    for i in range(0, len(encoded_text), 8):
        byte = encoded_text[i:i + 8]
        if len(byte) < 8:
            byte += '0' * (8 - len(byte))
        byte_array.append(int(byte, 2))

    with open(filename, 'wb') as f:
        frequency_lines = [f"{ord(char)}:{freq}" for char, freq in zip(alphabet, frequency_list)]
        f.write((' '.join(frequency_lines) + '\n').encode('utf-8'))
        f.write(byte_array)

def read_from_binary_file(filename):
    with open(filename, 'rb') as f:
        line = f.readline()
        frequency = []
        alphabet = []
        freq_data = line.decode('utf-8').strip().split(' ')

        for item in freq_data:
            if ':' in item:
                char_code, freq = item.split(':')
                char = chr(int(char_code.strip()))
                alphabet.append(char)
                frequency.append(int(freq.strip()))
        encoded_text = ''.join(format(byte, '08b') for byte in f.read())
        print(encoded_text)
        return frequency, encoded_text, alphabet

if __name__ == "__main__":
    def main(input_filename, output_filename):
        action = input("Вы хотите закодировать или декодировать текст? (введите 'encode' или 'decode'): ").strip().lower()
        if action == 'encode':
            with open(input_filename, 'r', encoding='utf-8') as file:
                text = file.read()
            text+=ArithmeticCoder.BREAK_SYMBOL

            coder = ArithmeticCoder(text)
            coder.print_table()

            encoded_text = coder.arithmetic_encoding()
            print("Закодированный текст:", encoded_text)
            original_size = len(text) * 8
            compressed_size = len(encoded_text)
            compression_ratio = original_size / compressed_size if compressed_size > 0 else float('inf')

            print(f"Размер исходного текста: {original_size} бит")
            print(f"Размер закодированного текста: {compressed_size} бит")
            print(f"Коэффициент сжатия: {compression_ratio:.2f}")

            write_to_binary_file(encoded_text, coder.frequency, coder.alphabet, output_filename)

            print("Закодированный текст успешно записан в", output_filename)


        elif action == 'decode':
            frequency, encoded_text, alphabet = read_from_binary_file(output_filename)
            coder = ArithmeticCoder('')
            coder.alphabet = alphabet
            coder.frequency = frequency
            print(coder.frequency)
            decoded_text = coder.arithmetic_decoding(encoded_text)
            print("Декодированный текст:", decoded_text)
            endfile = open('output.txt', 'w', encoding='utf-8')
            endfile.write(decoded_text)
            print("Декодированный текст записан в output.txt")

        else:
            print("Неверный выбор. Пожалуйста, введите 'encode' или 'decode'.")

    input_filename = 'Pivo.txt'
    output_filename = 'output.bin'
    main(input_filename, output_filename)
