import os
import yaml

from ipm import IPM


def config_parser():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str,  default="config_ptz.yaml", help="config file")
    parser.add_argument("--image_dir", type=str, help="image directiory")
    parser.add_argument("--output_dir", type=str, help="output directiory")
    parser.add_argument("--image_width", type=int, help="image width")
    parser.add_argument("--image_height", type=int, help="image height")
    parser.add_argument("--resize", nargs="+", type=int, help="image resize scale for save after IPM")
    parser.add_argument("--vanish_line", type=int, help="vanish line row")
    parser.add_argument("--world_width", type=float, help="world width, unit:m")
    parser.add_argument("--world_height", type=float, help="world height, unit:m")
    parser.add_argument("--world_pixel", type=float, help="world pixel, unit:m")
    parser.add_argument("--world_y_start", type=float, help="world y start, unit:m")
    parser.add_argument("--intrinsic", nargs="+", type=float, help="camera intrinsic parameters fx,fy,cx,cy")
    parser.add_argument("--Rcw", nargs="+", type=float, help="rotation matrix from world to camera")
    parser.add_argument("--tcw", nargs="+", type=float, help="translation vector from world to camera")

    return parser


def parser_config(name):
    import yaml

    cwd = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(cwd, "config", name)) as file:
        cfg = yaml.safe_load(file)

    return cfg


def main():
    parser = config_parser()
    args = parser.parse_args()
    cfg = parser_config(args.config)

    if args.image_dir is not None:
        cfg["image_dir"] = args.image_dir
    if args.output_dir is not None:
        cfg["output_dir"] = args.output_dir
    if args.image_width is not None:
        cfg["image_width"] = args.image_width
    if args.image_height is not None:
        cfg["image_height"] = args.image_height
    if args.resize is not None:
        cfg["resize"] = args.resize
    if args.vanish_line is not None:
        cfg["vanish_line"] = args.vanish_line
    if args.world_width is not None:
        cfg["world_width"] = args.world_width
    if args.world_height is not None:
        cfg["world_height"] = args.world_height
    if args.world_pixel is not None:
        cfg["world_pixel"] = args.world_pixel
    if args.world_y_start is not None:
        cfg["world_y_start"] = args.world_y_start
    if args.intrinsic is not None:
        cfg["intrinsic"] = args.intrinsic
    if args.Rcw is not None:
        cfg["Rcw"] = args.Rcw
    if args.tcw is not None:
        cfg["tcw"] = args.tcw
    print(f"[main] {args.config} >> \n{cfg}")

    ipm = IPM(cfg)
    ipm.transform()


if __name__=="__main__":
    main()
