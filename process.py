def load_fcs(fname):
    data=np.genfromtxt(fname,skip_header=2, skip_footer=1,usecols=(0,1,3))
    return data
    
def load_lsm(fname):
    data=np.genfromtxt(fname,skip_header=0, skip_footer=0,usecols=(1,2,3))
    return data
