import yaml
import ipm

def config_parser():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str,  default='./config_3840x2160.yaml', help='config_file')
    parser.add_argument("--image-dir", type=str, default='./data/images', help='input image directiory')
    parser.add_argument("--output-dir", type=str, default='./output', help='output directiory')
    parser.add_argument("--resize", nargs='+', type=int, help='image resize scale for save after IPM')
    # parser.add_argument("--width", type=int, default=960, help='image width')
    # parser.add_argument("--height", type=int, default=540, help='image height')
    # parser.add_argument("--channel", type=int, default=1, help='image channel')
    parser.add_argument("--width", type=int, default=3840, help='image width')
    parser.add_argument("--height", type=int, default=2160, help='image height')
    parser.add_argument("--channel", type=int, default=3, help='image channel')
    # parser.add_argument("--vanish_line", type=int, default=280, help='vanish line row')
    parser.add_argument("--vanish_line", type=int, default=1120, help='vanish line row')
    parser.add_argument("--ipm_width_x_3d", type=float, default=30.0, help='ipm range 3d x, unit:m')
    parser.add_argument("--ipm_height_y_3d", type=float, default=8.0, help='ipm range 3d y, unit:m')
    # parser.add_argument("--ipm_step_xy", type=float, default=0.04, help='ipm step 3d, unit:m')
    parser.add_argument("--ipm_step_xy", type=float, default=0.01, help='ipm step 3d, unit:m')
    parser.add_argument("--ipm_height_y_start", type=float, default=3.0, help='ipm start 3d y, unit:m')
    parser.add_argument("--intrinsic", nargs='+', type=float, help='input camera intrinsic parameters fx,fy,cx,cy')
    parser.add_argument("--R_ccs2ocs", nargs='+', type=float, help='rotation matrix from ccs to ocs')
    parser.add_argument("--T_ccs2ocs", nargs='+', type=float, help='translation vector from ccs to ocs')

    return parser

def main():
    parser = config_parser()
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    print(f"{args.config}:\n{cfg}")

    if cfg.get('image_dir') is not None:
        args.image_dir = cfg['image_dir']
    if cfg.get('output_dir') is not None:
        args.output_dir = cfg['output_dir']
    if cfg.get('width') is not None:
        args.width = cfg['width']
    if cfg.get('height') is not None:
        args.height = cfg['height']
    if cfg.get('channel') is not None:
        args.channel = cfg['channel']
    if cfg.get('resize') is not None:
        args.resize = cfg['resize']
    if cfg.get('vanish_line') is not None:
        args.vanish_line = cfg['vanish_line']
    if cfg.get('ipm_width_x_3d') is not None:
        args.ipm_width_x_3d = cfg['ipm_width_x_3d']
    if cfg.get('ipm_height_y_3d') is not None:
        args.ipm_height_y_3d = cfg['ipm_height_y_3d']
    if cfg.get('ipm_step_xy') is not None:
        args.ipm_step_xy = cfg['ipm_step_xy']
    if cfg.get('ipm_height_y_start') is not None:
        args.ipm_height_y_start = cfg['ipm_height_y_start']
    if cfg.get('intrinsic') is not None:
        args.intrinsic = cfg['intrinsic']
    elif args.intrinsic is None:
        args.intrinsic = [2141.9937, 2144.1709, 1724.7345, 1106.3953]
    if cfg.get('R_ccs2ocs') is not None:
        args.R_ccs2ocs = cfg['R_ccs2ocs']
    elif args.R_ccs2ocs is None:
        args.R_ccs2ocs = [0.999616, -0.00817016, 0.0264734,
                          0.0263923, -0.00988875, -0.999603,
                          0.0084287, 0.999918, -0.00966933]
    if cfg.get('T_ccs2ocs') is not None:
        args.T_ccs2ocs = cfg['T_ccs2ocs']
    elif args.T_ccs2ocs is None:
        args.T_ccs2ocs = [-0.498692, 1.619, 2.51533]

    # # 960x540
    # if args.intrinsic is None:
    #     args.intrinsic = [476.2483, 477.0686, 484.8964, 262.8846]
    # if args.R_ccs2ocs is None:
    #     args.R_ccs2ocs = [0.9937560081539198, 0.1109831719351175, 0.01147744767823091, 
    #                       0.003276455792956701, 0.07379581423704455, -0.9972679893782455, 
    #                       -0.111526952327333, 0.9910786615341447, 0.07297140231806608]
    # if args.T_ccs2ocs is None:
    #     args.T_ccs2ocs = [0.2317971025971608, 1.713913045205863, 1.913995241236965]
    
    # # 3840x2160
    # if args.intrinsic is None:
    #     args.intrinsic = [2141.9937, 2144.1709, 1724.7345, 1106.3953]
    # if args.R_ccs2ocs is None:
    #     args.R_ccs2ocs = [0.999616, -0.00817016, 0.0264734,
    #                       0.0263923, -0.00988875, -0.999603,
    #                       0.0084287, 0.999918, -0.00966933]
    # if args.T_ccs2ocs is None:
    #     args.T_ccs2ocs = [-0.498692, 1.619, 2.51533]

    # 找到IPM图像上对应到原始图像上的四个边界点
    model = ipm.IPM(args)
    model.get_ipm_images()

    return

if __name__=="__main__":
    main()
