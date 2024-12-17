import jpype
import jpype.imports
from jpype.types import *
import sys
import pandas as pd
from joblib import load

def extract_img(img_path):
    from com.google.zxing import BinaryBitmap, ResultMetadataType
    from com.google.zxing.client.j2se import BufferedImageLuminanceSource
    from com.google.zxing.common import HybridBinarizer
    from com.google.zxing.qrcode.decoder import BitMatrixParser, ErrorCorrectionLevel, Version, DataBlock
    from com.google.zxing.qrcode.detector import Detector
    from com.google.zxing.qrcode import QRCodeReader

    import java.io.File
    from javax.imageio import ImageIO

    cols = [
            'Version',
            'Error Correction Level',
            'Number of Blocks',
            'Expected number of data codewords',
            'Actual number of data codewords',
            'Number of empty bytes',
            'Number of EC Codewords',
            'Errors corrected',
    ]

    df = pd.DataFrame(columns=cols)

    try:
        file = java.io.File(img_path)
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
        versionNumber = version.getVersionNumber()

        codewords = parser.readCodewords()
        dataBlocks = DataBlock.getDataBlocks(codewords, version, ecLevel)

        reader = QRCodeReader()
        result = reader.decode(binaryBitmap)
        metadata = result.getResultMetadata()
        corrected = metadata.get(ResultMetadataType.ERRORS_CORRECTED)

        totalExpectedDataCodewords = 0
        totalActualDataCodewords = 0
        totalEmptyBytesData = 0
        concatenatedDataCodewords = []

        for i, dataBlock in enumerate(dataBlocks):
            codewordBytes = dataBlock.getCodewords()
            numDataCodewords = dataBlock.getNumDataCodewords()

            dataBytes = codewordBytes[:numDataCodewords]
            ecBytes = codewordBytes[numDataCodewords:]

            nonZeroDataBytes = [b for b in dataBytes if b != 0x00]

            emptyBytesDataSize = len(dataBytes) - len(nonZeroDataBytes)

            totalExpectedDataCodewords += len(dataBytes)
            totalActualDataCodewords += len(nonZeroDataBytes)
            totalEmptyBytesData += emptyBytesDataSize
            concatenatedDataCodewords.extend(nonZeroDataBytes)

        entry = pd.DataFrame([{
                'Version': versionNumber,
                'Error Correction Level': ecLevel.toString(),
                'Number of Blocks': len(dataBlocks),
                'Expected number of data codewords': totalExpectedDataCodewords,
                'Actual number of data codewords': totalActualDataCodewords,
                'Number of empty bytes': totalEmptyBytesData,
                'Number of EC Codewords': len(ecBytes),
                'Errors corrected': corrected,
        }])
        df = pd.concat([df, entry], ignore_index=True)

    except jpype.JException as je:
        print("Java exception occurred:")
        je.printStackTrace()
    except Exception as e:
        print(f"Exception occurred: {e}")
    
    return df


def validate(path_to_model, data):
    model = load(path_to_model)

    df = data
    df['EC Level'] = df['Error Correction Level'].map(
    {'L': 1, 'M': 2, 'Q': 3, 'H': 4}).astype(int)
    tc = df[['Version', 'EC Level', 'Expected number of data codewords',
              'Actual number of data codewords', 'Errors corrected']]

    tc = tc.apply(pd.to_numeric).astype(int)
    verdict = model.predict(tc)

    return verdict


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python backend_poc.py <path_to_image>")
    else:
        jpype.startJVM(classpath=['zxing/core/target/core-3.5.3.jar', 'zxing/javase/target/javase-3.5.3.jar'])
        data = extract_img(sys.argv[1])
        verdict = validate("model.xz", data)
        print(verdict) # Just pure verdict for now 
        jpype.shutdownJVM()
