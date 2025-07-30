"""
How to run:

uv run python aspredwrapper.py

or

uv run python aspredwrapper.py --infpath inference_directory --modelpath model_directory
"""

import argparse
import mysql.connector
import csv
import subprocess
import os
import random
import sys
from datetime import datetime

from dotenv import load_dotenv


def parse_arguments():
    parser = argparse.ArgumentParser(description='Path configuration for aspred')
    parser.add_argument('--infpath', 
                       type=str,
                       default='/Users/sb/projects/aspred/aspredFE/aspredINF/',
                       help='Path to the inference directory')
    parser.add_argument('--modelpath', 
                       type=str,
                       default='/Users/sb/projects/aspred/aspredFE/aspredINF/',                       
                       help='Path to the model directory')
    
    args = parser.parse_args()
    
    # Verify if the paths exist
    if not os.path.exists(args.infpath):
        raise ValueError(f"Inference path does not exist: {args.infpath}")
    if not os.path.exists(args.modelpath):
        raise ValueError(f"Model path does not exist: {args.modelpath}")
        
    return args.infpath, args.modelpath

# Use it in your code
INFPATH, MODELPATH = parse_arguments()


curdir = os.getcwd()
predfile = 'forASPRED.csv'
predictedfile = predfile.split('.')[0] + '__thresh0.5_predictions.csv' 
load_dotenv('.env.prod')
db_config = {
        'user': 'sbassimain',
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'database': 'aspred'
    }


def generate_aspred_input(config):

    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Query to get pending sequences
        query = """
        SELECT id, sequence 
        FROM sequence_analyzer_sequencesubmission 
        WHERE status = 'pending'
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        if not results:
            print("No new sequences to run the inference")
            sys.exit(1)
        id_lst = [row[0] for row in results]
        
        with open(predfile, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['sequence','_'])
            for _, sequence in results:
                writer.writerow([sequence, 0])
        
        print(f"Created {predfile} with {len(results)} sequences")
        print(f"ID list contains {len(id_lst)} IDs")
        
        return id_lst
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        print("Exiting due to an error")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()



def run_prediction():
    print("Running prediction script...")
    subprocess.run(['uv', 'run', 'python', os.path.join(INFPATH, 'run_new_set.py'), 
                    '--model_path', MODELPATH, 
                    '--input_csv', os.path.join(curdir, predfile)],
                    cwd=INFPATH)


def run_prediction_test():
    """Create mock predictions file"""
    try:
        with open(predfile, 'r', newline='') as infile:
            reader = csv.reader(infile)
            sequences = list(reader)
        with open(predictedfile, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['sequence', 'label', 'predicted_probs', 'predicted_labels'])
            for sequence, label in sequences:
                prob = random.random()
                pred_label = 1 if prob >= 0.5 else 0
                writer.writerow([sequence, label, prob, pred_label])
        print("Created mock predictions file: forASPRED_predictions.csv")
    except FileNotFoundError:
        print("Error: forASPRED.csv not found")
    except Exception as e:
        print(f"Error creating predictions file: {e}")


def read_output():
    """Read the third column from the predictions CSV file"""
    predictions = []
    try:
        with open(predictedfile, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                if len(row) >= 3:
                    predictions.append(row[3]) 
        return predictions
    except FileNotFoundError:
        print(f"Error: {predictedfile} not found 105")
        return []
    except Exception as e:
        print(f"Error reading predictions file: {e}")
        return []


def update_database(id_lst, predictions, config):
    """Update the database with prediction results"""

    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        now = datetime.now()
        for id_val, prediction in zip(id_lst, predictions):
            result = float(prediction)
            query = """
            UPDATE sequence_analyzer_sequencesubmission
            SET result = %s, result_date = %s, status = 'done'
            WHERE id = %s
            """
            cursor.execute(query, (result, now, id_val))
        conn.commit()
        print(f"Updated {len(id_lst)} rows in the database")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    id_lst = generate_aspred_input(db_config)
    print("ID list:", id_lst)
    run_prediction()
    #run_prediction_test()
    preds_lst = read_output()
    print(preds_lst)
    update_database(id_lst, preds_lst, db_config)

