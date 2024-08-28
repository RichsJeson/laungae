import numpy as np
import tensorflow as tf
import numpy as np

if __name__ == '__main__':
    # # 读取文件
    # with open('1.txt', 'rb') as f:
    #     data = f.read()
    #
    # # 将文件分割为数据包
    # packets = [data[i:i + 966] for i in range(0, len(data), 966)]
    #
    # # 将每个数据包转换为训练数据和标签
    # train_data = np.array([list(packet) for packet in packets])
    # train_labels = np.ones(len(packets))
    #
    # # 保存训练数据和标签为.npy文件
    # np.save('train_data.npy', train_data)
    # np.save('train_labels.npy', train_labels)

    # 加载训练数据和标签
    train_data = np.load('train_data.npy')
    train_labels = np.load('train_labels.npy')

    # 训练神经网络模型
    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(train_data, train_labels, epochs=10)

    # 读取输入文件并将其分割成数据包
    with open('1.txt', 'rb') as f:
        data = f.read()
        packets = []
        i = 0
        while i < len(data):
            if data[i:i + 2] == b'\xd0\x00':
                packet = data[i:i + 966]
                packets.append(packet)
                i += 966
            else:
                i += 1

    # 将每个数据包转换为训练数据和标签
    X = []
    y = []
    for packet in packets:
        channel = packet[0]
        sequence = int.from_bytes(packet[2:4], byteorder='little')
        data = packet[4:964]
        checksum = int.from_bytes(packet[964:966], byteorder='little')
        checkpacket = packet[0:964]
        # 计算checksum
        sum = 0
        for i in range(len(checkpacket)):
            sum += checkpacket[i] & 0xFF  # 这里我们直接使用 checkpacket[i] ，因为你已经确保它是一个字节
        checksum2 = sum & 0xFFFF
        print("checksum2:" + str(checksum2))
        checksum = int.from_bytes(packet[964:], byteorder='little')
        print("checksum:" + str(checksum))
        if checksum2 == checksum:
            X.append(data)
            y.append(1)

    # 校验和纠正数据包
    for i in range(len(packets)):
        packet = packets[i]
        channel = packet[0]
        sequence = int.from_bytes(packet[2:4], byteorder='little')
        data = packet[4:964]
        checksum = int.from_bytes(packet[964:], byteorder='little')
        sum = 0
        for i in range(len(checkpacket)):
            sum += checkpacket[i] & 0xFF  # 这里我们直接使用 checkpacket[i] ，因为你已经确保它是一个字节
        checksum2 = sum & 0xFFFF
        if checksum != checksum2:
            # 如果 data 的长度小于 966，这里需要适当的处理，例如截取或填充数据
            data_reshaped = np.reshape(data, (1, 964))  # 将数据重塑为(1, 966)的形状
            corrected_data = model.predict(data_reshaped)
            # 如果 corrected_data 是一个 numpy 数组，使用 np.sum()
            packets[i] = bytes([channel]) + b'\x00\x00' + corrected_data.tobytes() + b'\x00\x00' + bytes(
                [np.sum(corrected_data) % 65536])  # 使用 np.sum() 进行求和操作

    # 匹配数据包
    matched_packets = []
    for packet in packets:
        channel = packet[0]
        sequence = int.from_bytes(packet[2:4], byteorder='little')
        data = packet[4:964]
        checksum = int.from_bytes(packet[964:], byteorder='little')
        print("checksum:"+checksum)
        matched = False
        for i in range(len(train_data)):
            if sum(train_data[i]) % 65536 == checksum:
                matched_packets.append(train_data[i])
                matched = True
                break
        if not matched:
            matched_packets.append(None)

    # 按照序号排序
    sorted_packets = [packet for _, packet in
                      sorted(zip([int.from_bytes(packet[2:4], byteorder='little') for packet in packets], packets))]

    # 将所有数据包写入新文件中
    with open('output.txt', 'wb') as f:
        for packet in sorted_packets:
            f.write(packet)