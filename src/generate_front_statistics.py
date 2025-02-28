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

def get_elbow(data):
    if (data["right_wrist"][0] != "NONE" and data["right_elbow"][0] != "NONE"):
        arm_length = math.sqrt((data["right_wrist"][0][0] - data["right_elbow"][0][0])**2 + (data["right_wrist"][0][1] - data["right_elbow"][0][1])**2)
    elif (data["left_wrist"][0] != "NONE" and data["left_elbow"][0] != "NONE"):
        arm_length = math.sqrt((data["left_wrist"][0][0] - data["left_elbow"][0][0])**2 + (data["left_wrist"][0][1] - data["left_elbow"][0][1])**2)
    else: 
        print("ERROR: elbow/wrist joints cannot be detected")
        return -1
    
    if (data["left_elbow"] != "NONE") and (data["right_elbow"] != "NONE"):
        left_entry = data["left_elbow"]
        right_entry = data["right_elbow"]
        return (abs(((left_entry[1]) - (right_entry[1])) / arm_length))

def compare_front(data, hse_ra_params, hse_la_params, sew_ra_params, sew_la_params, ewa_ra_params, ewp_la_params, elbow_params):
    # hip-shoulder-elbow right arm
    if ((data["right_hip"] != "NONE") and (data["right_shoulder"] != "NONE") and (data["right_elbow"] != "NONE")):
        angle_hse_ra = calculate_angle(data["right_shoulder"], data["right_hip"], data["right_elbow"])
    
    # hip-shoulder-elbow left arm
    if ((data["left_hip"] != "NONE") and (data["left_shoulder"] != "NONE") and (data["left_elbow"] != "NONE")):
        angle_hse_la = calculate_angle(data["left_shoulder"], data["left_hip"], data["left_elbow"])

    # shoulder-elbow-wrist right arm
    if ((data["right_shoulder"] != "NONE") and (data["right_elbow"] != "NONE") and (data["right_wrist"] != "NONE")):
        angle_sew_ra = calculate_angle(data["right_elbow"], data["right_shoulder"], data["right_wrist"])
    
    # shoulder-elbow-wrist left arm
    if ((data["left_shoulder"] != "NONE") and (data["left_elbow"] != "NONE") and (data["left_wrist"] != "NONE")):
        angle_sew_la = calculate_angle(data["left_elbow"], data["left_shoulder"], data["left_wrist"])
    
    # elbow-wrist-average right arm (avg = thumb and pinky)
    if ((data["right_elbow"] != "NONE") and (data["right_wrist"] != "NONE")):
        if (data["right_pinky"] != "NONE" and data["right_thumb"] != "NONE"):
            x = (data["right_pinky"][0] + data["right_thumb"][0]) / 2
            y = (data["right_pinky"][1] + data["right_thumb"][1]) / 2
            coord = [x, y]
            angle_ewa_ra = calculate_angle(data["right_wrist"], data["right_elbow"], coord)

    # elbow-wrist-pinky left arm
    if ((data["left_elbow"] != "NONE") and (data["left_wrist"] != "NONE") and (data["left_pinky"] != "NONE")):
        angle_ewp_la = calculate_angle(data["left_wrist"], data["left_elbow"], data["left_pinky"])
    
    # hse: Angle at shoulder using points: hip, shoulder, left_elbow.
    pdf_hse_ra_new = beta.pdf(angle_hse_ra/180.0, hse_ra_params["alpha"], hse_ra_params["beta"])
    pdf_hse_la_new = beta.pdf(angle_hse_la/180.0, hse_la_params["alpha"], hse_la_params["beta"])
    pdf_hse_ra_mean = beta.pdf(hse_ra_params["mean"]/180.0, hse_ra_params["alpha"], hse_ra_params["beta"])
    pdf_hse_la_mean = beta.pdf(hse_la_params["mean"]/180.0, hse_la_params["alpha"], hse_la_params["beta"])
    score_hse_ra = (pdf_hse_ra_new / pdf_hse_ra_mean) * 100 if pdf_hse_ra_mean != 0 else 0
    score_hse_la = (pdf_hse_la_new / pdf_hse_la_mean) * 100 if pdf_hse_la_mean != 0 else 0
    score_hse_ra = max(0, min(100, score_hse_ra))
    score_hse_la = max(0, min(100, score_hse_la))
    
    # sew: Angle at left_elbow using points: shoulder, left_elbow, wrist.
    pdf_sew_ra_new = beta.pdf(angle_sew_ra/180.0, sew_ra_params["alpha"], sew_ra_params["beta"])
    pdf_sew_la_new = beta.pdf(angle_sew_la/180.0, sew_la_params["alpha"], sew_la_params["beta"])
    pdf_sew_ra_mean = beta.pdf(sew_ra_params["mean"]/180.0, sew_ra_params["alpha"], sew_ra_params["beta"])
    pdf_sew_la_mean = beta.pdf(sew_la_params["mean"]/180.0, sew_la_params["alpha"], sew_la_params["beta"])
    score_sew_ra = (pdf_sew_ra_new / pdf_sew_ra_mean) * 100 if pdf_sew_ra_mean != 0 else 0
    score_sew_la = (pdf_sew_la_new / pdf_sew_la_mean) * 100 if pdf_sew_la_mean != 0 else 0
    score_sew_ra = max(0, min(100, score_sew_ra))
    score_sew_la = max(0, min(100, score_sew_la))
    
    # ewa: Angle at wrist using points: right elbow, wrist, average between thumb and pinky
    pdf_ewa_ra_new = beta.pdf(angle_ewa_ra/180.0, ewa_ra_params["alpha"], ewa_ra_params["beta"])
    pdf_ewa_ra_mean = beta.pdf(ewa_ra_params["mean"]/180.0, ewa_ra_params["alpha"], ewa_ra_params["beta"])
    score_ewa_ra = (pdf_ewa_ra_new / pdf_ewa_ra_mean) * 100 if pdf_ewa_ra_mean != 0 else 0
    score_ewa_ra = max(0, min(100, score_ewa_ra))

    # ewp: Angle at wrist using points: left_elbow, wrist, pinky.
    pdf_ewp_la_new = beta.pdf(angle_ewp_la/180.0, ewp_la_params["alpha"], ewp_la_params["beta"])
    pdf_ewp_la_mean = beta.pdf(ewp_la_params["mean"]/180.0, ewp_la_params["alpha"], ewp_la_params["beta"])
    score_ewp_la = (pdf_ewp_la_new / pdf_ewp_la_mean) * 100 if pdf_ewp_la_mean != 0 else 0
    score_ewp_la = max(0, min(100, score_ewp_la))
    
    # ec: Use the calculate_elbow function.
    ec_value = get_elbow(data)

    # For ec, values are already in [0,1], so no scaling is needed.
    pdf_ec_new = beta.pdf(ec_value, elbow_params["alpha"], elbow_params["beta"])
    pdf_ec_mean = beta.pdf(elbow_params["mean"], elbow_params["alpha"], elbow_params["beta"])
    score_ec = (pdf_ec_new / pdf_ec_mean) * 100 if pdf_ec_mean != 0 else 0
    score_ec = max(0, min(100, score_ec))
    
    return {
        "hse_ra_score": score_hse_ra,
        "hse_la_score": score_hse_la,
        "sew_ra_score": score_sew_ra,
        "sew_la_score": score_sew_la,
        "ewa_ra_score": score_ewa_ra,
        "ewp_la_score": score_ewp_la,
        "ec_score": score_ec
    }

def get_klay_data():
    return {'left_shoulder': [805, 735], 'right_shoulder': [821, 737], 'left_elbow': None, 'right_elbow': [927, 758], 'left_wrist': None, 'right_wrist': [899, 838], 'left_hip': [779, 531], 'right_hip': [787, 533], 'left_pinky': None, 'right_pinky': [886, 862], 'left_thumb': None, 'right_thumb': [874, 847], 'ball': None, 'Side': 'RIGHT', 'frame': 52}

def get_params():
    hse_ra_params = {'mean': 43.298923816434325, 'std': 40.25967787806732, 'alpha': 0.6378923208507256, 'beta': 2.0139199560527907}
    hse_la_params = {'mean': 92.8862314104217, 'std': 18.213527582489963, 'alpha': 12.071157105814251, 'beta': 11.32098881348697}
    sew_ra_params = {'mean': 56.513779392939966, 'std': 43.3325881553567, 'alpha': 0.8529125252622869, 'beta': 1.8636683899824433}
    sew_la_params = {'mean': 69.94910046694802, 'std': 25.983045238195032, 'alpha': 4.0424297033764995, 'beta': 6.359953483117646}
    ewa_ra_params = {'mean': 171.2429226074844, 'std': 2.700463421634448, 'alpha': 194.67860198702382, 'beta': 9.955538940285523}
    ewp_la_params = {'mean': 166.53889329592488, 'std': 9.400764569916712, 'alpha': 22.544792995353788, 'beta': 1.8222642058302212}
    elbow_params = {'mean': 0.1860944586520072, 'std': 0.07193177550894218, 'alpha': 5.261431738885052, 'beta': 23.011477497621666}

    return hse_ra_params, hse_la_params, sew_ra_params, sew_la_params, ewa_ra_params, ewp_la_params, elbow_params
def main():
    # Compute similarity scores for front view.
    new_front_data = get_klay_data()
    hse_ra_params, hse_la_params, sew_ra_params, sew_la_params, ewa_ra_params, ewp_la_params, elbow_params = get_params()
    front_scores = compare_front(new_front_data, hse_ra_params, hse_la_params, sew_ra_params, sew_la_params, ewa_ra_params, ewp_la_params, elbow_params)
    
    print("Front view similarity scores:")
    print(front_scores)

if __name__ == "__main__":
    main()
