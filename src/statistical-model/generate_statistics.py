from scipy.stats import beta
import math

def calculate_angle(vertex, a, b):
    """
    Calculate the angle (in degrees) between three points: a -> vertex -> b.
    """
    AV = (a[0] - vertex[0], a[1] - vertex[1])
    BV = (b[0] - vertex[0], b[1] - vertex[1])
    
    dot_product = AV[0] * BV[0] + AV[1] * BV[1]
    AV_magnitude = math.sqrt(AV[0]**2 + AV[1]**2)
    BV_magnitude = math.sqrt(BV[0]**2 + BV[1]**2)
    
    if AV_magnitude == 0 or BV_magnitude == 0:
        return 0.0
    
    cos_value = max(min(dot_product / (AV_magnitude * BV_magnitude), 1.0), -1.0)
    return math.degrees(math.acos(cos_value))

def compare_arm(new_data, which_arm, sew_params, ewa_params):
    """
    Computes similarity scores (0-100) for the specified arm based on the new shot's angles
    and the provided Beta distribution parameters.
    
    Inputs:
        new_data  : dict with keys "shoulder", "elbow", "wrist", "pinky", "index"
        which_arm : string "left" or "right" (for identification)
        sew_params: dict for Shoulder-Elbow-Wrist angle in the form 
                    {"mean": mean_val, "std": std_val, "alpha": alpha_val, "beta": beta_val}
        ewa_params: dict for Elbow-Wrist-Average(Pinky,Index) angle, same format as sew_params.
    
    Process:
        - Computes the shoulder–elbow–wrist (sew) angle and the elbow–wrist–average(Pinky, Index) (ewa) angle.
        - For each angle, scales it to the [0,1] interval by dividing by 180.
        - Evaluates the Beta PDF at the computed angle and at the mean.
        - Computes the score as:
              score = (BetaPDF(new_angle/180) / BetaPDF(mean/180)) * 100
          and clamps the result between 0 and 100.
    
    Returns:
        A dictionary with keys:
          "sew_score": similarity score for the sew angle,
          "ewa_score": similarity score for the ewa angle.
    """
    # Extract coordinates from new_data.
    shoulder = new_data[f"{which_arm}_shoulder"]
    elbow = new_data[f"{which_arm}_elbow"]
    wrist = new_data[f"{which_arm}_wrist"]
    pinky = new_data[f"{which_arm}_pinky"]
    index = new_data[f"{which_arm}_index"]
    
    # Calculate the shoulder–elbow–wrist (sew) angle.
    angle_sew = calculate_angle(elbow, shoulder, wrist)
    
    # Calculate the elbow–wrist–average(Pinky,Index) (ewa) angle.
    avg_pinky_index = [(pinky[0] + index[0]) / 2, (pinky[1] + index[1]) / 2]
    angle_ewa = calculate_angle(wrist, elbow, avg_pinky_index)
    
    # For sew: scale angles to [0,1]
    sew_mean = sew_params["mean"]
    sew_alpha = sew_params["alpha"]
    sew_beta  = sew_params["beta"]
    
    # Evaluate Beta PDF at computed sew angle and at the mean (scaled by 180).
    pdf_sew_new = beta.pdf(angle_sew / 180.0, sew_alpha, sew_beta)
    pdf_sew_mean = beta.pdf(sew_mean / 180.0, sew_alpha, sew_beta)
    score_sew = (pdf_sew_new / pdf_sew_mean) * 100 if pdf_sew_mean != 0 else 0
    
    # For ewa: scale angles to [0,1]
    ewa_mean = ewa_params["mean"]
    ewa_alpha = ewa_params["alpha"]
    ewa_beta  = ewa_params["beta"]
    
    pdf_ewa_new = beta.pdf(angle_ewa / 180.0, ewa_alpha, ewa_beta)
    pdf_ewa_mean = beta.pdf(ewa_mean / 180.0, ewa_alpha, ewa_beta)
    score_ewa = (pdf_ewa_new / pdf_ewa_mean) * 100 if pdf_ewa_mean != 0 else 0
    
    # Clamp scores between 0 and 100.
    score_sew = max(0, min(100, score_sew))
    score_ewa = max(0, min(100, score_ewa))
    
    return {
        "sew_score": score_sew,
        "ewa_score": score_ewa
    }

def main():
    # Dummy distribution parameters for the left arm.
    left_sew_params = {"mean": 45.0, "std": 5.0, "alpha": 2.0, "beta": 3.0}
    left_ewa_params = {"mean": 50.0, "std": 6.0, "alpha": 2.5, "beta": 3.5}
    
    # Dummy distribution parameters for the right arm.
    right_sew_params = {"mean": 40.0, "std": 4.0, "alpha": 1.8, "beta": 2.8}
    right_ewa_params = {"mean": 55.0, "std": 7.0, "alpha": 3.0, "beta": 4.0}
    
    # Combined dummy new shot data for both arms in a single dictionary.
    new_arm_data = {
        "left_shoulder": [100, 200],
        "left_elbow": [110, 250],
        "left_wrist": [120, 300],
        "left_pinky": [125, 305],
        "left_index": [123, 307],
        "right_shoulder": [200, 200],
        "right_elbow": [210, 250],
        "right_wrist": [220, 300],
        "right_pinky": [225, 305],
        "right_index": [223, 307]
    }
    
    # Compute similarity scores for both arms.
    left_scores = compare_arm(new_arm_data, "left", left_sew_params, left_ewa_params)
    right_scores = compare_arm(new_arm_data, "right", right_sew_params, right_ewa_params)
    
    print("Left arm similarity scores:")
    print(left_scores)
    
    print("Right arm similarity scores:")
    print(right_scores)

if __name__ == "__main__":
    main()