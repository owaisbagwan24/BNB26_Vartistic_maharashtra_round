import csv
from ast_engine import analyze_code_and_error

def run_eval():
    with open('../dataset/misconceptions.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        correct = 0
        total = 0
        for row in reader:
            total += 1
            res = analyze_code_and_error(row['student_code'], row['error_message'], row['wrong_output'])
            expected = row['misconception_id']
            pred = res['label'] if res else 'None'
            matched = (pred == expected)
            if matched:
                correct += 1
            print(f"{row['id']}: expected={expected} pred={pred} matched={matched}")
        print(f"\nDeterministic Rule/AST Accuracy on Gold Samples: {correct}/{total} ({correct/total*100:.1f}%)")

if __name__ == '__main__':
    run_eval()
