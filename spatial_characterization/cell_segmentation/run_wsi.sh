python run_infer.py \
--gpu='1' \
--nr_types=3 \
--type_info_path=type_info.json \
--model_mode=original \
--model_path=./logs/net_epoch=50.tar \
--nr_inference_workers=8 \
--nr_post_proc_workers=16 \
wsi \
--chunk_shape=5120 \
--tile_shape=1024 \
--input_dir=/DataMount/xl260/Megan_Scanner/WSI_1 \
--output_dir=/DataMount/xl260/Megan_Scanner/Out_1 \
--input_mask_dir=/DataMount/xl260/Megan_Scanner/Output2/mask2 \

# --save_mask \


# --input_mask_dir=/DataMount/NEPTUNE/output0908/mask32_NEPTUNE \

#--save_thumb \


