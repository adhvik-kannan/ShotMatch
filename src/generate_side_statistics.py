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

def compare_side_ra(data, sew_ra_params, ewp_ra_params):
    # shoulder-elbow-wrist right arm
    if ((data["right_shoulder"] != "NONE") and (data["right_elbow"] != "NONE") and (data["right_wrist"] != "NONE")):
        angle_sew_ra = calculate_angle(data["right_elbow"], data["right_shoulder"], data["right_wrist"])

    # elbow-wrist-pinky right arm
    if ((data["right_elbow"] != "NONE") and (data["right_wrist"] != "NONE") and (data["right_pinky"] != "NONE")):
        angle_ewp_ra = calculate_angle(data["right_wrist"], data["right_elbow"], data["right_pinky"])
    
    # sew: Angle at left_elbow using points: shoulder, left_elbow, wrist.
    pdf_sew_ra_new = beta.pdf(angle_sew_ra/180.0, sew_ra_params["alpha"], sew_ra_params["beta"])
    pdf_sew_ra_mean = beta.pdf(sew_ra_params["mean"]/180.0, sew_ra_params["alpha"], sew_ra_params["beta"])
    score_sew_ra = (pdf_sew_ra_new / pdf_sew_ra_mean) * 100 if pdf_sew_ra_mean != 0 else 0
    score_sew_ra = max(0, min(100, score_sew_ra))
    
    # ewp: Angle at wrist using points: right_elbow, wrist, pinky.
    pdf_ewp_ra_new = beta.pdf(angle_ewp_ra/180.0, ewp_ra_params["alpha"], ewp_ra_params["beta"])
    pdf_ewp_ra_mean = beta.pdf(ewp_ra_params["mean"]/180.0, ewp_ra_params["alpha"], ewp_ra_params["beta"])
    score_ewp_ra = (pdf_ewp_ra_new / pdf_ewp_ra_mean) * 100 if pdf_ewp_ra_mean != 0 else 0
    score_ewp_ra = max(0, min(100, score_ewp_ra))

    return {
        "sew_ra_score": score_sew_ra,
        "ewp_ra_score": score_ewp_ra,
    }

def compare_side_la(data, sew_la_params, ewa_la_params):
    # shoulder-elbow-wrist left arm
    if ((data["left_shoulder"] != "NONE") and (data["left_elbow"] != "NONE") and (data["left_wrist"] != "NONE")):
        angle_sew_la = calculate_angle(data["left_elbow"], data["left_shoulder"], data["left_wrist"])

    # elbow-wrist-average left arm (avg = thumb and pinky)
    if ((data["left_elbow"] != "NONE") and (data["left_wrist"] != "NONE")):
        if (data["left_pinky"] != "NONE" and data["left_thumb"] != "NONE"):
            x = (data["left_pinky"][0] + data["left_thumb"][0]) / 2
            y = (data["left_pinky"][1] + data["left_thumb"][1]) / 2
            coord = [x, y]
            angle_ewa_la = calculate_angle(data["left_wrist"], data["left_elbow"], coord)

    
    # sew: Angle at left_elbow using points: shoulder, left_elbow, wrist.
    pdf_sew_la_new = beta.pdf(angle_sew_la/180.0, sew_la_params["alpha"], sew_la_params["beta"])
    pdf_sew_la_mean = beta.pdf(sew_la_params["mean"]/180.0, sew_la_params["alpha"], sew_la_params["beta"])
    score_sew_la = (pdf_sew_la_new / pdf_sew_la_mean) * 100 if pdf_sew_la_mean != 0 else 0
    score_sew_la = max(0, min(100, score_sew_la))
    
    # ewa: Angle at wrist using points: left elbow, wrist, average between thumb and pinky
    pdf_ewa_la_new = beta.pdf(angle_ewa_la/180.0, ewa_la_params["alpha"], ewa_la_params["beta"])
    pdf_ewa_la_mean = beta.pdf(ewa_la_params["mean"]/180.0, ewa_la_params["alpha"], ewa_la_params["beta"])
    score_ewa_la = (pdf_ewa_la_new / pdf_ewa_la_mean) * 100 if pdf_ewa_la_mean != 0 else 0
    score_ewa_la = max(0, min(100, score_ewa_la))
    
    return {
        "sew_la_score": score_sew_la,
        "ewa_la_score": score_ewa_la
    }

def get_klay_data():
    return {'left_shoulder': [805, 735], 'right_shoulder': [821, 737], 'left_elbow': None, 'right_elbow': [927, 758], 'left_wrist': None, 'right_wrist': [899, 838], 'left_hip': [779, 531], 'right_hip': [787, 533], 'left_pinky': None, 'right_pinky': [886, 862], 'left_thumb': None, 'right_thumb': [874, 847], 'ball': None, 'Side': 'RIGHT', 'frame': 52}

def main():
    print("temp")

if __name__ == "__main__":
    main()