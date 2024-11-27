import os
import jpype
import jpype.imports
from jpype.types import *
import sys
import csv

def main(directory_path, output_path, ds_type):
    jpype.startJVM(classpath=['zxing/core/target/core-3.5.3.jar', 'zxing/javase/target/javase-3.5.3.jar'])

    from com.google.zxing import BinaryBitmap, ResultMetadataType
    from com.google.zxing.client.j2se import BufferedImageLuminanceSource
    from com.google.zxing.common import HybridBinarizer
    from com.google.zxing.qrcode.decoder import BitMatrixParser, ErrorCorrectionLevel, Version, DataBlock
    from com.google.zxing.qrcode.detector import Detector
    from com.google.zxing.qrcode import QRCodeReader

    import java.io.File
    from javax.imageio import ImageIO

    data = []

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            file = java.io.File(file_path)
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
                translatedEcBytes = [b for b in ecBytes if b != 0x00]

                emptyBytesDataSize = len(dataBytes) - len(nonZeroDataBytes)

                totalExpectedDataCodewords += len(dataBytes)
                totalActualDataCodewords += len(nonZeroDataBytes)
                totalEmptyBytesData += emptyBytesDataSize
                concatenatedDataCodewords.extend(nonZeroDataBytes)

            entry = {
                    'Version': versionNumber,
                    'Error Correction Level': ecLevel.toString(),
                    'Number of Blocks': len(dataBlocks),
                    'Expected number of data codewords': totalExpectedDataCodewords,
                    'Actual number of data codewords': totalActualDataCodewords,
                    'Number of empty bytes': totalEmptyBytesData,
                    'Number of EC Codewords': len(ecBytes),
                    'Errors corrected': corrected,
                    'Modified': ds_type,
            }
            data.append(entry)

        except jpype.JException as je:
            print(f"Java exception occurred while processing {filename}:")
            je.printStackTrace()
        except Exception as e:
            print(f"Exception occurred while processing {filename}: {e}")
    
    dump_to_csv(data, output_path)
    jpype.shutdownJVM()

def dump_to_csv(csv_data, target):
    csv_file = target
    with open(csv_file, mode='w', newline='') as file:
        fieldnames = [
            'Version',
            'Error Correction Level',
            'Number of Blocks',
            'Expected number of data codewords',
            'Actual number of data codewords',
            'Number of empty bytes',
            'Number of EC Codewords',
            'Errors corrected',
            'Modified',
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for r in csv_data:
            writer.writerow(r)


def usage():
    print("Usage: python generate_csv.py <source_dir> <output_file> <dataset_type>")
    print("Options for <dataset_type>:")
    print("0 - benign")
    print("1 - malicious")
 

if __name__ == '__main__':
    if len(sys.argv) < 4:
        usage()
    else:
        if sys.argv[3] not in ["0", "1"]:
            usage()
        else:
            main(sys.argv[1], sys.argv[2], sys.argv[3])
