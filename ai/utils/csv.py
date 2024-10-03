import os
import pandas as pd

def find_and_convert_csv_to_json(output_dir):
    # output_dir에서 CSV 파일 찾기
    csv_files = [file for file in os.listdir(output_dir) if file.endswith('.csv')]

    # 파일이 작성된 시간순으로 정렬
    csv_files.sort(key=lambda file: os.path.getmtime(os.path.join(output_dir, file)))

    # 가장 최근에 작성된 파일을 불러옴
    csv_file_path = os.path.join(output_dir, csv_files[-1])

    # CSV 파일 읽기
    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        return {"error": "CSV file not found in the specified directory."}
    except Exception as e:
        return {"error": f"Error reading CSV file: {str(e)}"}

    result = {
        "global_step": df["global_step"].tolist(),
        "loss": df["loss"].tolist(),
        "learning_rate": df["learning_rate"].tolist()
    }

    return result