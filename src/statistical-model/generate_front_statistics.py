from scipy.stats import beta
import math

def calculate_angle(vertex, a, b):
    """
    Calculate the angle (in degrees) between three points: a -> vertex -> b.
    
    Inputs:
        a       = point 1 (e.g., hip for hse, shoulder for sew, or elbow for ewp)
        vertex  = point 2 (e.g., shoulder for hse, elbow for sew, or wrist for ewp)
        b       = point 3 (e.g., elbow for hse, wrist for sew, or pinky for ewp)
    
    Output:
        Angle in degrees between a -> vertex -> b.
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

def calculate_elbow(new_data):
    """
    Calculates the elbow comparison metric from front-view data.
    
    This metric is computed as:
         EC = |left_elbow_y - right_elbow_y| / (distance between left_wrist and left_elbow)
    
    Inputs:
        new_data: dictionary containing keys "left_elbow", "right_elbow", and "left_wrist"
                  with values as [x, y] coordinates.
                  
    Returns:
        The elbow comparison ratio (a float between 0 and 1, ideally).
    """
    left_elbow = new_data["left_elbow"]
    right_elbow = new_data["right_elbow"]
    left_wrist = new_data["wrist"]  # Note: for front view, we assume left wrist is used for length.
    
    diff_y = abs(left_elbow[1] - right_elbow[1])
    length_left_arm = math.sqrt((left_wrist[0] - left_elbow[0])**2 + (left_wrist[1] - left_elbow[1])**2)
    if length_left_arm == 0:
        return 0.0
    return diff_y / length_left_arm

def compare_front(new_data, hse_params, sew_params, ewp_params, ec_params):
    """
    Computes similarity scores (0-100) for front-view metrics based on new data and 
    the provided Beta distribution parameters. The metrics include:
      - hse: Hip -> Shoulder -> Left Elbow angle (vertex = shoulder)
      - sew: Shoulder -> Left Elbow -> Wrist angle (vertex = left elbow)
      - ewp: Left Elbow -> Wrist -> Pinky angle (vertex = wrist)
      - ec : Elbow Comparison metric (computed using calculate_elbow)
    
    For each metric, the new value is scaled to the [0,1] interval (by dividing by 180 for angles;
    for ec, values are already in [0,1]), then the Beta PDF is evaluated at the new value and the 
    stored mean. The similarity score is computed as:
          score = (BetaPDF(new_value) / BetaPDF(mean)) * 100
    and clamped between 0 and 100.
    
    Inputs:
        new_data : dict with keys "hip", "shoulder", "left_elbow", "right_elbow", "wrist", "pinky"
        hse_params: Beta distribution parameters for Hip-Shoulder-Elbow angle
        sew_params: Beta distribution parameters for Shoulder-Elbow-Wrist angle
        ewp_params: Beta distribution parameters for Elbow-Wrist-Pinky angle
        ec_params : Beta distribution parameters for Elbow Comparison metric (values in [0,1])
    
    Returns:
        A dictionary with keys:
          "hse_score", "sew_score", "ewp_score", "ec_score"
    """
    # Extract coordinates.
    hip = new_data["hip"]
    shoulder = new_data["shoulder"]
    left_elbow = new_data["left_elbow"]
    # right_elbow is used only for the elbow comparison metric.
    right_elbow = new_data["right_elbow"]
    wrist = new_data["wrist"]
    pinky = new_data["pinky"]
    
    # hse: Angle at shoulder using points: hip, shoulder, left_elbow.
    angle_hse = calculate_angle(shoulder, hip, left_elbow)
    pdf_hse_new = beta.pdf(angle_hse/180.0, hse_params["alpha"], hse_params["beta"])
    pdf_hse_mean = beta.pdf(hse_params["mean"]/180.0, hse_params["alpha"], hse_params["beta"])
    score_hse = (pdf_hse_new / pdf_hse_mean) * 100 if pdf_hse_mean != 0 else 0
    score_hse = max(0, min(100, score_hse))
    
    # sew: Angle at left_elbow using points: shoulder, left_elbow, wrist.
    angle_sew = calculate_angle(left_elbow, shoulder, wrist)
    pdf_sew_new = beta.pdf(angle_sew/180.0, sew_params["alpha"], sew_params["beta"])
    pdf_sew_mean = beta.pdf(sew_params["mean"]/180.0, sew_params["alpha"], sew_params["beta"])
    score_sew = (pdf_sew_new / pdf_sew_mean) * 100 if pdf_sew_mean != 0 else 0
    score_sew = max(0, min(100, score_sew))
    
    # ewp: Angle at wrist using points: left_elbow, wrist, pinky.
    angle_ewp = calculate_angle(wrist, left_elbow, pinky)
    pdf_ewp_new = beta.pdf(angle_ewp/180.0, ewp_params["alpha"], ewp_params["beta"])
    pdf_ewp_mean = beta.pdf(ewp_params["mean"]/180.0, ewp_params["alpha"], ewp_params["beta"])
    score_ewp = (pdf_ewp_new / pdf_ewp_mean) * 100 if pdf_ewp_mean != 0 else 0
    score_ewp = max(0, min(100, score_ewp))
    
    # ec: Use the calculate_elbow function.
    ec_value = calculate_elbow(new_data)
    # For ec, values are already in [0,1], so no scaling is needed.
    pdf_ec_new = beta.pdf(ec_value, ec_params["alpha"], ec_params["beta"])
    pdf_ec_mean = beta.pdf(ec_params["mean"], ec_params["alpha"], ec_params["beta"])
    score_ec = (pdf_ec_new / pdf_ec_mean) * 100 if pdf_ec_mean != 0 else 0
    score_ec = max(0, min(100, score_ec))
    
    return {
        "hse_score": score_hse,
        "sew_score": score_sew,
        "ewp_score": score_ewp,
        "ec_score": score_ec
    }

def main():
    # Dummy distribution parameters for front view angles.
    hse_params = {"mean": 30.0, "std": 4.0, "alpha": 1.5, "beta": 2.0}
    sew_params = {"mean": 45.0, "std": 5.0, "alpha": 2.0, "beta": 3.0}
    ewp_params = {"mean": 60.0, "std": 6.0, "alpha": 2.5, "beta": 3.5}
    # Dummy distribution parameters for elbow comparison metric (ec), values in [0,1].
    ec_params = {"mean": 0.1, "std": 0.05, "alpha": 2.0, "beta": 8.0}
    
    # Dummy new front view data.
    # For simplicity, we assume each key holds a single [x, y] coordinate.
    new_front_data = {
        "hip": [90, 180],
        "shoulder": [100, 200],
        "left_elbow": [110, 250],
        "right_elbow": [115, 255],
        "wrist": [120, 300],
        "pinky": [125, 305]
    }
    
    # Compute similarity scores for front view.
    front_scores = compare_front(new_front_data, hse_params, sew_params, ewp_params, ec_params)
    
    print("Front view similarity scores:")
    print(front_scores)

if __name__ == "__main__":
    main()
