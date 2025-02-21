import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.stats import beta

NUM_CLIPS = 0

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

def process_front_data(hip, shoulder, left_elbow, right_elbow, wrist, pinky):
    """
    Processes frames of front-view data and computes four arrays:
      - hse: Hip -> Shoulder -> Elbow angles (vertex = shoulder)
      - sew: Shoulder -> Elbow -> Wrist angles (vertex = elbow)
      - ewp: Elbow -> Wrist -> Pinky angles (vertex = wrist)
      - ec : Elbow Comparison metric = (|left_elbow_y - right_elbow_y|) / (distance between left_wrist and left_elbow)
    
    Inputs:
        hip         = list of hip coordinates
        shoulder    = list of shoulder coordinates
        left_elbow  = list of left elbow coordinates
        right_elbow = list of right elbow coordinates
        wrist       = list of wrist coordinates
        pinky       = list of pinky coordinates
        
    Outputs:
        hse_array, sew_array, ewp_array, ec_array as numpy arrays.
    """
    hse_list = []
    sew_list = []
    ewp_list = []
    ec_list = []
    
    for i in range(len(hip)):
        h = hip[i]
        s = shoulder[i]
        le = left_elbow[i]
        re = right_elbow[i]
        w = wrist[i]
        p = pinky[i]
        
        # Hip-Shoulder-Elbow (hse): angle at shoulder using points: hip, shoulder, left_elbow.
        angle_hse = calculate_angle(s, h, le)
        hse_list.append(angle_hse)
        
        # Shoulder-Elbow-Wrist (sew): angle at left_elbow using points: shoulder, left_elbow, wrist.
        angle_sew = calculate_angle(le, s, w)
        sew_list.append(angle_sew)
        
        # Elbow-Wrist-Pinky (ewp): angle at wrist using points: left_elbow, wrist, pinky.
        angle_ewp = calculate_angle(w, le, p)
        ewp_list.append(angle_ewp)
        
        # Elbow Comparison (ec):
        # Compute absolute difference in y-coordinate between left_elbow and right_elbow.
        diff_y = abs(le[1] - re[1])
        # Calculate length of left arm: distance between left_elbow and wrist.
        length_left_arm = math.sqrt((w[0] - le[0])**2 + (w[1] - le[1])**2)
        if length_left_arm == 0:
            ec = 0.0
        else:
            ec = diff_y / length_left_arm
        ec_list.append(ec)
    
    return np.array(hse_list), np.array(sew_list), np.array(ewp_list), np.array(ec_list)

def calculate_distribution_parameters(angles, max_val=180):
    """
    Calculates distribution parameters for a given set of values by scaling
    them to the [0,1] interval and fitting a Beta distribution.
    
    Inputs:
        angles  = numpy array of values (in degrees by default; for ratios, adjust max_val)
        max_val = maximum value (default is 180 for angles; for ratios use 1)
    
    Outputs:
        A dictionary containing:
            - mean: sample mean
            - std: sample standard deviation
            - alpha: Beta distribution alpha parameter
            - beta: Beta distribution beta parameter
    """
    mean_val = float(np.mean(angles))
    std_val = float(np.std(angles))
    m_y = mean_val / max_val
    s_y_sq = (std_val**2) / (max_val**2)
    
    if s_y_sq <= 0:
        alpha = beta_val = 100
    else:
        factor = (m_y * (1 - m_y) / s_y_sq) - 1
        alpha = m_y * factor
        beta_val = (1 - m_y) * factor
    
    return {"mean": mean_val, "std": std_val, "alpha": alpha, "beta": beta_val}

def generate_front_plot(dist_params_hse, dist_params_sew, dist_params_ewp, dist_params_ec, view_name="front", save_plot=True):
    """
    Generates and (optionally) saves a plot of the weighted bell curves for the front-view metrics,
    using a Beta distribution scaled to [0,180] for angle metrics and [0,1] for the elbow comparison.
    
    Inputs:
        dist_params_hse = distribution parameters for Hip-Shoulder-Elbow angles.
        dist_params_sew = distribution parameters for Shoulder-Elbow-Wrist angles.
        dist_params_ewp = distribution parameters for Elbow-Wrist-Pinky angles.
        dist_params_ec  = distribution parameters for the Elbow Comparison metric (max_val assumed to be 1).
        view_name       = name of the view, default "front".
        save_plot       = if True, the plot is saved to file.
    """
    # For the angle metrics, we use the [0,180] domain.
    x_angles = np.linspace(0, 180, 200)
    y_hse = (1/180.0) * beta.pdf(x_angles/180.0, dist_params_hse["alpha"], dist_params_hse["beta"])
    y_sew = (1/180.0) * beta.pdf(x_angles/180.0, dist_params_sew["alpha"], dist_params_sew["beta"])
    y_ewp = (1/180.0) * beta.pdf(x_angles/180.0, dist_params_ewp["alpha"], dist_params_ewp["beta"])
    
    # For the elbow comparison, we assume values in [0,1].
    x_ec = np.linspace(0, 1, 200)
    y_ec = beta.pdf(x_ec, dist_params_ec["alpha"], dist_params_ec["beta"])
    
    plt.figure(figsize=(10, 6))
    plt.plot(x_angles, y_hse, label='Hip-Shoulder-Elbow', color='green')
    plt.plot(x_angles, y_sew, label='Shoulder-Elbow-Wrist', color='blue')
    plt.plot(x_angles, y_ewp, label='Elbow-Wrist-Pinky', color='red')
    plt.plot(x_ec, y_ec, label='Elbow Comparison', color='purple')
    plt.title(f'Weighted Bell Curves for {view_name.capitalize()} View Metrics\n(Beta Distribution)')
    plt.xlabel('Value')
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True)
    
    if save_plot:
        plot_filename = f"{view_name}_view_bell_curve.png"
        plt.savefig(plot_filename)
        print(f"Saved {view_name} view bell curve plot to '{plot_filename}'")
    plt.close()

def main():
    # Dummy data for front view (3 frames for demonstration; typically 20+ frames)
    hip = [[90, 180], [91, 181], [92, 182]]
    shoulder = [[100, 200], [101, 201], [102, 202]]
    left_elbow = [[110, 250], [111, 251], [112, 252]]
    right_elbow = [[115, 255], [116, 256], [117, 257]]
    wrist = [[120, 300], [121, 301], [122, 302]]
    pinky = [[125, 305], [126, 306], [127, 307]]
    
    # Process front view data to compute four metrics.
    angle_hse, angle_sew, angle_ewp, elbow_comp = process_front_data(hip, shoulder, left_elbow, right_elbow, wrist, pinky)
    
    # Calculate distribution parameters for each metric.
    dist_params_hse = calculate_distribution_parameters(angle_hse)         # Using default max_val=180.
    dist_params_sew = calculate_distribution_parameters(angle_sew)         # Using default max_val=180.
    dist_params_ewp = calculate_distribution_parameters(angle_ewp)         # Using default max_val=180.
    dist_params_ec = calculate_distribution_parameters(elbow_comp, max_val=1)  # For ratios, max_val=1.
    
    # Generate the plot for front view.
    generate_front_plot(dist_params_hse, dist_params_sew, dist_params_ewp, dist_params_ec, view_name="front")
    
    # Print the computed distribution parameters.
    print("Front view Hip-Shoulder-Elbow parameters:", dist_params_hse)
    print("Front view Shoulder-Elbow-Wrist parameters:", dist_params_sew)
    print("Front view Elbow-Wrist-Pinky parameters:", dist_params_ewp)
    print("Front view Elbow Comparison parameters:", dist_params_ec)

if __name__ == "__main__":
    main()
