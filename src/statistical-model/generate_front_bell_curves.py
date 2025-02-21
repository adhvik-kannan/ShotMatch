import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.stats import beta

NUM_CLIPS = 0

def calculate_angle(vertex, a, b):
    """
    Calculate the angle (in degrees) between three points: a -> vertex -> b.
    
    Inputs:
        a       = point 1 (e.g., hip for hse or shoulder for sew)
        vertex  = point 2 (e.g., shoulder for hse, elbow for sew, wrist for ewp)
        b       = point 3 (e.g., elbow for hse, wrist for sew, pinky for ewp)
        
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

def process_front_data(hip, shoulder, elbow, wrist, pinky):
    """
    Processes frames of front-view data and computes three arrays:
      - hse: Hip -> Shoulder -> Elbow angles (calculated at the shoulder)
      - sew: Shoulder -> Elbow -> Wrist angles (calculated at the elbow)
      - ewp: Elbow -> Wrist -> Pinky angles (calculated at the wrist)
    
    Inputs:
        hip       = list of hip coordinates
        shoulder  = list of shoulder coordinates
        elbow     = list of elbow coordinates
        wrist     = list of wrist coordinates
        pinky     = list of pinky coordinates
        
    Outputs:
        angle_hse  = numpy array of hip-shoulder-elbow angles
        angle_sew  = numpy array of shoulder-elbow-wrist angles
        angle_ewp  = numpy array of elbow-wrist-pinky angles
    """
    angle_hse_list = []
    angle_sew_list = []
    angle_ewp_list = []
    
    for i in range(len(hip)):
        h = hip[i]
        s = shoulder[i]
        e = elbow[i]
        w = wrist[i]
        p = pinky[i]
        
        # Hip-Shoulder-Elbow (hse): vertex is shoulder.
        angle_hse = calculate_angle(s, h, e)
        angle_hse_list.append(angle_hse)
        
        # Shoulder-Elbow-Wrist (sew): vertex is elbow.
        angle_sew = calculate_angle(e, s, w)
        angle_sew_list.append(angle_sew)
        
        # Elbow-Wrist-Pinky (ewp): vertex is wrist.
        angle_ewp = calculate_angle(w, e, p)
        angle_ewp_list.append(angle_ewp)
    
    return (np.array(angle_hse_list), 
            np.array(angle_sew_list), 
            np.array(angle_ewp_list))

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

def generate_front_plot(dist_params_hse, dist_params_sew, dist_params_ewp, view_name="front", save_plot=True):
    """
    Generates and (optionally) saves a plot of the weighted bell curves for the front-view angles
    using a Beta distribution scaled to [0,180] degrees.
    
    Inputs:
        dist_params_hse = distribution parameters for Hip-Shoulder-Elbow angles.
        dist_params_sew = distribution parameters for Shoulder-Elbow-Wrist angles.
        dist_params_ewp = distribution parameters for Elbow-Wrist-Pinky angles.
        view_name       = name of the view, default "front".
        save_plot       = if True, the plot is saved to file.
    """
    x = np.linspace(0, 180, 200)
    
    # For hse
    alpha_hse = dist_params_hse["alpha"]
    beta_hse = dist_params_hse["beta"]
    y_hse = (1/180.0) * beta.pdf(x/180.0, alpha_hse, beta_hse)
    
    # For sew
    alpha_sew = dist_params_sew["alpha"]
    beta_sew = dist_params_sew["beta"]
    y_sew = (1/180.0) * beta.pdf(x/180.0, alpha_sew, beta_sew)
    
    # For ewp
    alpha_ewp = dist_params_ewp["alpha"]
    beta_ewp = dist_params_ewp["beta"]
    y_ewp = (1/180.0) * beta.pdf(x/180.0, alpha_ewp, beta_ewp)
    
    plt.figure(figsize=(10, 6))
    plt.plot(x, y_hse, label='Hip-Shoulder-Elbow', color='green')
    plt.plot(x, y_sew, label='Shoulder-Elbow-Wrist', color='blue')
    plt.plot(x, y_ewp, label='Elbow-Wrist-Pinky', color='red')
    plt.title(f'Weighted Bell Curves for {view_name.capitalize()} View Angles\n(Beta Distribution)')
    plt.xlabel('Angle (Degrees)')
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
    # Each list contains coordinates as [x, y] for each frame.
    hip = [[90, 180], [91, 181], [92, 182]]
    shoulder = [[100, 200], [101, 201], [102, 202]]
    elbow = [[110, 250], [111, 251], [112, 252]]
    wrist = [[120, 300], [121, 301], [122, 302]]
    pinky = [[125, 305], [126, 306], [127, 307]]
    
    # Process the front view data.
    angle_hse, angle_sew, angle_ewp = process_front_data(hip, shoulder, elbow, wrist, pinky)
    
    # Calculate distribution parameters for each set of angles.
    dist_params_hse = calculate_distribution_parameters(angle_hse)
    dist_params_sew = calculate_distribution_parameters(angle_sew)
    dist_params_ewp = calculate_distribution_parameters(angle_ewp)
    
    # Generate the plot for front view.
    generate_front_plot(dist_params_hse, dist_params_sew, dist_params_ewp, view_name="front")
    
    # Print the computed distribution parameters for debugging.
    print("Front view Hip-Shoulder-Elbow parameters:", dist_params_hse)
    print("Front view Shoulder-Elbow-Wrist parameters:", dist_params_sew)
    print("Front view Elbow-Wrist-Pinky parameters:", dist_params_ewp)

if __name__ == "__main__":
    main()
