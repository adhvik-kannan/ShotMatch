import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.stats import beta

NUM_CLIPS = 0

def calculate_angle(vertex, a, b):
    """
    Calculate angle (in degrees) for (a -> vertex -> b)

    Inputs:
        a       = point 1 (e.g., shoulder)
        vertex  = point 2 (e.g., elbow)
        b       = point 3 (e.g., wrist)

    Output:
        Angle in degrees between a -> vertex -> b.
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

def process_arm_data(shoulder, elbow, wrist, pinky, index):
    """
    Processes frames of data for one arm and computes two arrays:
      - sew: Shoulder -> Elbow -> Wrist angles (computed at the elbow)
      - ewa: Elbow -> Wrist -> Average(Pinky, Index) angles (computed at the wrist)
    
    Inputs: 
        shoulder    = list of shoulder coordinates 
        elbow       = list of elbow coordinates
        wrist       = list of wrist coordinates
        pinky       = list of pinky coordinates
        index       = list of index coordinates
    
    Outputs:
        angle_sew_list  = numpy array of angles for shoulder->elbow->wrist
        angle_ewa_list  = numpy array of angles for elbow->wrist->(avg of pinky and index)
    """
    angle_sew_list = []
    angle_ewa_list = []
    
    for i in range(len(shoulder)):
        s = shoulder[i]
        e = elbow[i]
        w = wrist[i]
        p = pinky[i]
        idx = index[i]
        
        # Calculate the shoulder-elbow-wrist angle.
        angle_sew = calculate_angle(e, s, w)
        angle_sew_list.append(angle_sew)
        
        # Calculate the elbow-wrist angle using the average of pinky and index.
        avg_pinky_index = [(p[0] + idx[0]) / 2, (p[1] + idx[1]) / 2]
        angle_ewa = calculate_angle(w, e, avg_pinky_index)
        angle_ewa_list.append(angle_ewa)
    
    return np.array(angle_sew_list), np.array(angle_ewa_list)

def calculate_distribution_parameters(angles, max_val=180):
    """
    Calculates distribution parameters for a given set of angles by scaling
    them to the [0,1] interval and fitting a Beta distribution.
    
    Inputs:
        angles  = numpy array of angles (in degrees)
        max_val = maximum angle value (default is 180)
    
    Outputs:
        A dictionary containing:
            - mean: sample mean (in degrees)
            - std: sample standard deviation (in degrees)
            - alpha: Beta distribution alpha parameter
            - beta: Beta distribution beta parameter
    """
    mean_val = float(np.mean(angles))
    std_val = float(np.std(angles))
    m_y = mean_val / max_val
    s_y_sq = (std_val**2) / (max_val**2)
    
    if s_y_sq <= 0:
        alpha = beta_val = 100  # default, very peaked
    else:
        factor = (m_y * (1 - m_y) / s_y_sq) - 1
        alpha = m_y * factor
        beta_val = (1 - m_y) * factor
    
    return {"mean": mean_val, "std": std_val, "alpha": alpha, "beta": beta_val}

def generate_plot(dist_params_sew, dist_params_ewa, arm_name, save_plot=True):
    """
    Generates and (optionally) displays/saves a plot of the weighted bell curves
    for the given distribution parameters using a Beta distribution scaled to [0,180].
    
    Inputs:
        dist_params_sew  = distribution parameters for shoulder-elbow-wrist angles
        dist_params_ewa  = distribution parameters for elbow-wrist-average angles
        arm_name         = string indicating the arm ("left" or "right")
        save_plot        = if True, the plot is saved to file
    """
    x = np.linspace(0, 180, 200)
    
    alpha_sew = dist_params_sew["alpha"]
    beta_sew = dist_params_sew["beta"]
    alpha_ewa = dist_params_ewa["alpha"]
    beta_ewa = dist_params_ewa["beta"]
    
    # Compute the Beta PDFs transformed to the [0,180] domain.
    y_sew = (1/180.0) * beta.pdf(x/180.0, alpha_sew, beta_sew)
    y_ewa = (1/180.0) * beta.pdf(x/180.0, alpha_ewa, beta_ewa)
    
    plt.figure(figsize=(10, 6))
    plt.plot(x, y_sew, label='Shoulder-Elbow-Wrist Angles', color='blue')
    plt.plot(x, y_ewa, label='Elbow-Wrist-Average(Pinky, Index) Angles', color='red')
    plt.title(f'Weighted Bell Curves for {arm_name.capitalize()} Arm Angles\n(Beta Distribution)')
    plt.xlabel('Angle (Degrees)')
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True)
    
    if save_plot:
        plot_filename = f"{arm_name}_arm_bell_curve.png"
        plt.savefig(plot_filename)
        print(f"Saved {arm_name} arm bell curve plot to '{plot_filename}'")
    plt.close()

def main():
    # Dummy data for left arm (3 frames for demonstration; typically 20+ frames)
    left_shoulder = [[100, 200], [101, 201], [102, 202]]
    left_elbow = [[110, 250], [111, 251], [112, 252]]
    left_wrist = [[120, 300], [121, 301], [122, 302]]
    left_pinky = [[125, 305], [126, 306], [127, 307]]
    left_index = [[123, 307], [124, 308], [125, 309]]
    
    # Dummy data for right arm (3 frames for demonstration)
    right_shoulder = [[200, 200], [201, 201], [202, 202]]
    right_elbow = [[210, 250], [211, 251], [212, 252]]
    right_wrist = [[220, 300], [221, 301], [222, 302]]
    right_pinky = [[225, 305], [226, 306], [227, 307]]
    right_index = [[223, 307], [224, 308], [225, 309]]
    
    # returns angle arrays
    left_angle_sew, left_angle_ewa = process_arm_data(left_shoulder, left_elbow, left_wrist, left_pinky, left_index)
    right_angle_sew, right_angle_ewa = process_arm_data(right_shoulder, right_elbow, right_wrist, right_pinky, right_index)
    
    # dist parameters 
    left_dist_params_sew = calculate_distribution_parameters(left_angle_sew)
    left_dist_params_ewa = calculate_distribution_parameters(left_angle_ewa)
    right_dist_params_sew = calculate_distribution_parameters(right_angle_sew)
    right_dist_params_ewa = calculate_distribution_parameters(right_angle_ewa)
    
    # plots
    generate_plot(left_dist_params_sew, left_dist_params_ewa, "left")
    generate_plot(right_dist_params_sew, right_dist_params_ewa, "right")
    
    print("Left arm Shoulder-Elbow-Wrist parameters:", left_dist_params_sew)
    print("Left arm Elbow-Wrist-Average parameters:", left_dist_params_ewa)
    print("Right arm Shoulder-Elbow-Wrist parameters:", right_dist_params_sew)
    print("Right arm Elbow-Wrist-Average parameters:", right_dist_params_ewa)
    

if __name__ == "__main__":
    main()
