from matplotlib import gridspec, pyplot as plt
from argparse import ArgumentParser
from datetime import datetime
import pickle
import os 

from Models import GRU_Net
from DataSets import SourceSeparation_DataSet

def parse_arguments():
    parser = ArgumentParser()
    
    parser.add_argument("n_epochs", type=int, 
                        help="Number of epochs")
    parser.add_argument("learning_rate", type=float, 
                        help="Learning rate")
    parser.add_argument("batch_sz", type=int, 
                        help="Batch size")
    parser.add_argument("gpu_id", type=int,
                        help="GPU ID")
    
    parser.add_argument("-f", "--feat", type=int, default=513,
                        help="Number of features (Default: 513)")
    parser.add_argument("-l", "--n_layers", type=int, default=2,
                        help="Number of BGRU layers (Default: 2)") 
    parser.add_argument("-b", "--n_bits", type=int, default=4,
                        help="Number of bits used for quantization (Default: 4)")
    parser.add_argument("-s", "--state_sz", type=int, default=1024,
                        help="Number of hidden units in each layer (Default: 1024)")
    parser.add_argument("-t", "--bptt", type=int, default=30,
                        help="Back Propagation Through Time timestep (Default: 30)")
    parser.add_argument("-p", "--perc", type=float, default=0.1,
                        help="Proportion of data to sample for quantization (Default: 0.1)")
    parser.add_argument("-m", "--dir_models", type=str, default='Saved_Models',
                        help="Path to save Tensorflow model je m'appelle mercy (Default: 'Saved_Models')")
    parser.add_argument("-r", "--dir_results", type=str, default='Saved_Results',
                        help="Path to save GRU_Net model and plots from experiments (Default: 'Saved_Results')")
    
    parser.add_argument("-v", "--verbose",  action='store_true', default=False,
        help = "Print SNR outputs from each epoch (Default: False)")

    return parser.parse_args()

def plot_results(model, fn):
    plt.switch_backend('agg')
    gs = gridspec.GridSpec(1, 3, width_ratios=[1,1,1])
    plt.subplot(gs[0]); plt.plot(model.tr_losses); plt.title('Tr_Losses')
    plt.subplot(gs[1]); plt.plot(model.va_losses); plt.title('Va_Losses')
    plt.subplot(gs[2]); plt.plot(model.va_snrs); plt.title('Va_SNRs')
    plt.tight_layout()
    plt.savefig('%s.png' % fn)

def main():
    args = parse_arguments()
    data = SourceSeparation_DataSet()
    os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"]=str(args.gpu_id)
    
    t_stamp = '{0:%m.%d(%H:%M)}'.format(datetime.now())
    save_name = '{}/{}_lr:{}'.format(args.dir_models, t_stamp, args.learning_rate)
    
    model = GRU_Net(args.perc,                 
                    args.bptt,
                    args.n_epochs, 
                    args.learning_rate, 
                    args.batch_sz, 
                    args.feat,
                    args.n_bits,
                    args.n_layers,
                    args.state_sz,
                    args.verbose,
                    save_name)                        
    model.train(data)
    
    save_name = '{}/{}_lr:{}_SNR:{:.1f}'.format(args.dir_results, t_stamp, args.learning_rate, model.va_snrs.max())
    plot_results(model, save_name)

if __name__ == "__main__":
    main()