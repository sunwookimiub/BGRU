import tensorflow as tf
from argparse import ArgumentParser
from datetime import datetime
import _pickle as pickle
import logging
import os 
import re

from utils import *
from Models import GRU_Net
from DataSets import SourceSeparation_DataSet


def parse_arguments():
    parser = ArgumentParser()
    
    parser.add_argument("learning_rate", type=float, 
                        help="Learning rate")
    parser.add_argument("batch_sz", type=int, 
                        help="Batch size (multiples of number of noise signals)")
    parser.add_argument("bptt", type=int,
                        help="Back Propagation Through Time timestep")
    parser.add_argument("n_epochs", type=int, 
                        help="Number of epochs")
    parser.add_argument("gpu_id", type=int,
                        help="GPU ID")
    
    parser.add_argument("-b", "--n_bits", type=int, default=None,
                        help="Number of bits used for quantization (Default: None)")
    parser.add_argument("-c", "--clip_val", type=float, default=1.0,
                        help="Gradient clipping value)")
    parser.add_argument("-d", "--data_sz", type=str, default='small',
                        help="Size of data set (Default: small(2)). [Options: small(2), medium(4), large(8), xlarge(12)]")
    parser.add_argument("-e", "--is_pretrain", action='store_true',
                        help = "Use this option to pretrain")
    parser.add_argument("-g", "--gain", type=float, default=1.0,
                        help="GAIN to influence initialization stddev for the first layer of weights")
    parser.add_argument("-k", "--pickled_data", type=str, default=None,
                        help="Pretrained data to load")
    parser.add_argument("-l", "--n_layers", type=int, default=2,
                        help="Number of BGRU layers (Default: 2)")
    parser.add_argument("-m", "--dir_models", type=str, default='Saved_Models',
                        help="Path to save Tensorflow model je m'appelle mercy (Default: 'Saved_Models')")
    parser.add_argument("-n", "--n_noise", type=str, default='few',
                        help="Number of noise signals (Default: few(5)) [Options: few(5), many(10)]")
    parser.add_argument("-o", "--model_nm", type=str, default=None,
                        help="Pretrained model to load")
    parser.add_argument("-p", "--perc", type=float, default=0.1,
                        help="Proportion of data to sample for quantization (Default: 0.1)")
    parser.add_argument("-r", "--dir_results", type=str, default='Saved_Results',
                        help="Path to save GRU_Net model and plots from experiments (Default: 'Saved_Results')")
    parser.add_argument("-s", "--state_sz", type=int, default=1024,
                        help="Number of hidden units in each layer (Default: 1024)")
    parser.add_argument("-v", "--verbose",  action='store_true',
                        help = "Print SNR outputs from each epoch (Default: False)")
    parser.add_argument("-y", "--beta2", type=float, default=0.999,
                        help="Beta2 value for AdamOptimizer (Default: 0.999)")
    parser.add_argument("-z", "--beta1", type=float, default=0.9,
                        help="Beta1 value for AdamOptimizer (Default: 0.9)")

    return parser.parse_args()


def main():
    args = parse_arguments()
    logger = logging.getLogger(); logger.setLevel(logging.INFO)
    if args.pickled_data:
        with open(args.pickled_data, 'rb') as f:
            data = pickle.load(f)
        logger.info('Restoring data from {}'.format(args.pickled_data))
    else:
        data = SourceSeparation_DataSet(args.data_sz, args.n_noise)
    os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"]=str(args.gpu_id)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
    t_stamp = '{0:%m.%d(%H:%M)}'.format(datetime.now())
    
    is_restore = False
    if args.model_nm:
        is_restore = True
        run_info = mod_name(args.model_nm, args.n_epochs, args.is_pretrain, 1, args.learning_rate,
                            args.beta1, args.beta2, args.gain)
        args.model_nm = '{}/{}'.format(args.dir_models, args.model_nm)
    else:
        run_info = '{}_pretrain({})_batchsz({})_bptt({})_data({})_noise({})_bits({})'.format(
            t_stamp, args.is_pretrain, args.batch_sz, args.bptt, data.data_sz, data.n_noise, args.n_bits)
        args.model_nm = '{}/{}'.format(args.dir_models, run_info)

    model = GRU_Net(args.perc,                 
                    args.bptt,
                    args.n_epochs, 
                    args.learning_rate, 
                    args.beta1, 
                    args.beta2,
                    args.batch_sz, 
                    args.feat,
                    args.n_layers,
                    args.state_sz,
                    args.verbose,
                    is_restore,
                    args.model_nm,
                    args.n_bits,
                    args.is_pretrain,
                    args.gain,
                    args.clip_val)
    model.train(data)

    if is_restore:
        args.n_epochs = 0
    if args.is_pretrain:
        plot_name = '{}/{}'.format(args.dir_results, mod_name(run_info, args.n_epochs, args.is_pretrain, model.va_snrs.max(), args.learning_rate, args.beta1, args.beta2, args.gain))
    else:
        plot_name = '{}/{}'.format(args.dir_results, mod_name(run_info, args.n_epochs, args.is_pretrain, model.va_snrs.max()))
        # Do I need this?
    plot_results(model, plot_name)
    
if __name__ == "__main__":
    main()