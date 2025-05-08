python run_infer.py \
--gpu='0' \
--nr_types=3 \
--type_info_path=./type_info.json \
--model_mode=original \
--model_path=./logs/net_epoch=50.tar \
--nr_inference_workers=8 \
--nr_post_proc_workers=16 \
tile \
--input_dir="./test_data/input"  \
--output_dir="./test_data/output"