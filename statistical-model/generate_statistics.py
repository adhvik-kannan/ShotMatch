import json
import numpy as np
import math
from scipy.stats import norm


def calculate_angle(vertex, a, b):
    """
    calculate angle (degrees) for (a -> vertex -> b)

    """
    AV = (a[0] - vertex[0], a[1] - vertex[1])
    BV = (b[0] - vertex[0], b[1] - vertex[1])
    
    dot_product = AV[0]*BV[0] + AV[1]*BV[1]
    AV_magnitude = math.sqrt(AV[0]**2 + AV[1]**2)
    BV_magnitude = math.sqrt(BV[0]**2 + BV[1]**2)
    
    if AV_magnitude == 0 or BV_magnitude == 0:
        return 0.0
    
    cos_value = max(min(dot_product / (AV_magnitude * BV_magnitude), 1.0), -1.0)
    return math.degrees(math.acos(cos_value))


# ------------------------------------------------------------------------------------------------
# ISSUES - its on normal distribution rn but realistically your armor isnt bending past 0-180 range so maybe cap the distribution somehow
# ------------------------------------------------------------------------------------------------
def compare_arm(new_data, arm, distribution_params):
    """
    computes similarity percentage (1-100) for arm

    ewa: elbow -> wrist -> avg(index/pinky)
    sew: shoulder -> elbow -> wrist

    """
    shoulder = new_data[f"{arm}_shoulder"]
    elbow = new_data[f"{arm}_elbow"]
    wrist = new_data[f"{arm}_wrist"]
    pinky = new_data[f"{arm}_pinky"]
    index = new_data[f"{arm}_index"]
    
    # 2 angles
    angle_sew = calculate_angle(elbow, shoulder, wrist)
    avg_pinky_index = [(pinky[0] + index[0]) / 2, (pinky[1] + index[1]) / 2]
    angle_ewa = calculate_angle(wrist, elbow, avg_pinky_index)
    
    # get distribution params from file
    mean_sew = distribution_params["shoulder_elbow_wrist"]["mean"]
    std_sew = distribution_params["shoulder_elbow_wrist"]["std"]
    mean_ewa = distribution_params["elbow_wrist_avg_pinky_index"]["mean"]
    std_ewa = distribution_params["elbow_wrist_avg_pinky_index"]["std"]
    
    # similarity score based on PDF 
    score_sew = norm.pdf(angle_sew, mean_sew, std_sew) / norm.pdf(mean_sew, mean_sew, std_sew) * 100
    score_ewa = norm.pdf(angle_ewa, mean_ewa, std_ewa) / norm.pdf(mean_ewa, mean_ewa, std_ewa) * 100

    # Clamp scores between 1 and 100.
    score_sew = max(1, min(100, score_sew))
    score_ewa = max(1, min(100, score_ewa))
    
    return {
        "shoulder_elbow_wrist_score": score_sew,
        "elbow_wrist_avg_pinky_index_score": score_ewa
    }

def main():
    # get distribution params for the lfet and right arm
    try:
        with open("left_arm_angle_distribution.json", "r") as f_left:
            left_distribution = json.load(f_left)
    except FileNotFoundError:
        print("Error: 'left_arm_angle_distribution.json' not found. Please run the bell curve generator first.")
        return

    try:
        with open("right_arm_angle_distribution.json", "r") as f_right:
            right_distribution = json.load(f_right)
    except FileNotFoundError:
        print("Error: 'right_arm_angle_distribution.json' not found. Please run the bell curve generator first.")
        return

    # get data for shot we are trying to compare
    try:
        with open("new_shot_data.json", "r") as f_shot:
            new_shot_data = json.load(f_shot)
    except FileNotFoundError:
        print("Error: 'new_shot_data.json' not found. Please provide the new shot data.")
        return

    # get similarity scores
    left_arm_scores = compare_arm(new_shot_data, "left", left_distribution)
    right_arm_scores = compare_arm(new_shot_data, "right", right_distribution)
    
    # output intoi json file
    similarity_statistics = {
        "left_arm": left_arm_scores,
        "right_arm": right_arm_scores
    }
    
    output_filename = "shot_similarity_statistics.json"
    with open(output_filename, "w") as f_out:
        json.dump(similarity_statistics, f_out, indent=4)
    
    print(f"Similarity statistics saved to '{output_filename}'.")

if __name__ == "__main__":
    main()
