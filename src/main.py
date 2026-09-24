
from gen_synth_data import gen_synthetic_data
from bs_auto import bs_auto

if __name__ == "__main__":
  X, y, beta = gen_synthetic_data(24092026, 1000, 50, 48)
  bs_auto(X, y, 4)

