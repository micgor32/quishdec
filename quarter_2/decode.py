import sys
import jpype
import jpype.imports
from jpype.types import *


from com.google.zxing import BinaryBitmap
from com.google.zxing.client.j2se import BufferedImageLuminanceSource
from com.google.zxing.common import HybridBinarizer
from com.google.zxing.qrcode import QRCodeReader
from com.google.zxing.qrcode.decoder import BitMatrixParser, ErrorCorrectionLevel, Version, DataBlock 
from com.google.zxing.qrcode.detector import Detector
from com.google.zxing import ResultMetadataType

import java.io.File
from javax.imageio import ImageIO

def main(path):
    try:
        file = java.io.File(path)
        bufferedImage = ImageIO.read(file)

        luminanceSource = BufferedImageLuminanceSource(bufferedImage)
        binaryBitmap = BinaryBitmap(HybridBinarizer(luminanceSource))
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
            
        reader = QRCodeReader()
        result = reader.decode(binaryBitmap)
        corrected = result.getResultMetadata()
        print(corrected.get(ResultMetadataType.ERRORS_CORRECTED))

    except jpype.JException as je:
        print("A Java exception occurred:")
        je.printStackTrace()
    finally:
        # Shutdown the JVM
        jpype.shutdownJVM()


def usage():
    print("Usage: python decode.py <path_to_qr_code_img>")
 

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
    else:    
        jpype.startJVM(classpath=['zxing/core/target/core-3.5.3.jar', 'zxing/javase/target/javase-3.5.3.jar'])
        main(sys.argv[1])
