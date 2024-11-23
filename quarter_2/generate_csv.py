import jpype
import jpype.imports
from jpype.types import *

jpype.startJVM(classpath=['zxing/core/target/core-3.5.3.jar', 'zxing/javase/target/javase-3.5.3.jar'])

from com.google.zxing import BinaryBitmap
from com.google.zxing.client.j2se import BufferedImageLuminanceSource
from com.google.zxing.common import HybridBinarizer
from com.google.zxing.qrcode import QRCodeReader
from com.google.zxing.qrcode.decoder import BitMatrixParser, ErrorCorrectionLevel, Version, DataBlock
from com.google.zxing.qrcode.detector import Detector

import java.io.File
from javax.imageio import ImageIO

try:
    file = java.io.File('qrcode.png')
    bufferedImage = ImageIO.read(file)

    luminanceSource = BufferedImageLuminanceSource(bufferedImage)
    binaryBitmap = BinaryBitmap(HybridBinarizer(luminanceSource))

    # For testing purposes here, remove later
    # reader = QRCodeReader()
    # result = reader.decode(binaryBitmap)
    # print('Decoded text:', result.getText())


    bitMatrix = binaryBitmap.getBlackMatrix()
    detector = Detector(bitMatrix)
    detectorResult = detector.detect()
    correctedBitMatrix = detectorResult.getBits()
    parser = BitMatrixParser(correctedBitMatrix)

    formatInfo = parser.readFormatInformation()
    version = parser.readVersion()

    ecLevel = formatInfo.getErrorCorrectionLevel()
    print('Version:', version.getVersionNumber())
    print('Error Correction Level:', ecLevel)

    codewords = parser.readCodewords()

    dataBlocks = DataBlock.getDataBlocks(codewords, version, ecLevel)

    for i, dataBlock in enumerate(dataBlocks):
        codewordBytes = dataBlock.getCodewords()
        numDataCodewords = dataBlock.getNumDataCodewords()

        dataBytes = codewordBytes[:numDataCodewords]
        ecBytes = codewordBytes[numDataCodewords:]

        print(f"\nBlock {i+1}:")
        print(f"Data Codewords ({len(dataBytes)} bytes):", ' '.join(f"{b & 0xFF:02X}" for b in dataBytes))
        print(f"Error Correction Codewords ({len(ecBytes)} bytes):", ' '.join(f"{b & 0xFF:02X}" for b in ecBytes))

except jpype.JException as e:
    print("A Java exception occurred:")
    e.printStackTrace()
finally:
    jpype.shutdownJVM()

