import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt

class Args:
    total_timesteps: int = 1000000
    learning_rate: float = 1e-4
    batch_size: int = 64
    hidden_size: int = 64
    latent_size: int = 60
    num_epochs: int = 1000
    cuda: bool = True

args = Args()

device = torch.device("cuda" if torch.cuda.is_available() and args.cuda else "cpu")

class UPN(nn.Module):
    def __init__(self, state_dim, action_dim, latent_dim):
        super(UPN, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(state_dim, args.hidden_size),
            nn.ReLU(),
            nn.Linear(args.hidden_size, latent_dim)
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, args.hidden_size),
            nn.ReLU(),
            nn.Linear(args.hidden_size, state_dim)
        )

        # LSTM for forward dynamics
        self.dynamics_lstm = nn.LSTM(latent_dim + action_dim, args.hidden_size, batch_first=True)
        self.dynamics_fc = nn.Sequential(
            nn.ReLU(),
            nn.Linear(args.hidden_size, latent_dim)
        )

        # LSTM for inverse dynamics
        self.inverse_lstm = nn.LSTM(latent_dim * 2, args.hidden_size, batch_first=True)
        self.inverse_fc = nn.Sequential(
            nn.ReLU(),
            nn.Linear(args.hidden_size, action_dim)
        )

    def forward(self, state, action, next_state):
        # Encoding state and next state
        z = self.encoder(state)
        z_next = self.encoder(next_state)

        # Forward dynamics (z, action -> z_pred)
        dynamics_input = torch.cat([z, action], dim=-1)
        h_dynamics, _ = self.dynamics_lstm(dynamics_input) 
        z_pred = self.dynamics_fc(h_dynamics)

        # Inverse dynamics (z, z_next -> action_pred)
        inverse_input = torch.cat([z, z_next], dim=-1)
        h_inverse, _ = self.inverse_lstm(inverse_input)
        action_pred = self.inverse_fc(h_inverse)

        # Reconstruction of states
        state_recon = self.decoder(z)
        next_state_pred = self.decoder(z_pred)
        next_state_recon = self.decoder(z_next)

        return z, z_next, z_pred, action_pred, state_recon, next_state_recon, next_state_pred

def load_data(file_path='mvp/data/imitation_data_half_cheetah_5e6.npz'):
    data = np.load(file_path)
    states = torch.FloatTensor(data['states']).to(device)
    actions = torch.FloatTensor(data['actions']).to(device)
    next_states = torch.FloatTensor(data['next_states']).to(device)
    return states, actions, next_states

def compute_upn_loss(upn, state, action, next_state):
    z, z_next, z_pred, action_pred, state_recon, next_state_recon, next_state_pred = upn(state, action, next_state)
    recon_loss = nn.MSELoss()(state_recon, state) + nn.MSELoss()(next_state_recon, next_state)
    consistency_loss = nn.MSELoss()(next_state_pred, next_state)
    forward_loss = nn.MSELoss()(z_pred, z_next.detach())
    inverse_loss = nn.MSELoss()(action_pred, action)
    total_loss = recon_loss + forward_loss + inverse_loss + consistency_loss
    return total_loss, recon_loss, forward_loss, inverse_loss, consistency_loss

def train_model(model, dataloader, optimizer):
    model.train()
    total_loss = 0
    total_recon_loss = 0
    total_forward_loss = 0
    total_inverse_loss = 0
    total_consistency_loss = 0
    for states, actions, next_states in dataloader:
        optimizer.zero_grad()
        loss, recon_loss, forward_loss, inverse_loss, consistency_loss = compute_upn_loss(model, states, actions, next_states)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        total_recon_loss += recon_loss.item()
        total_forward_loss += forward_loss.item()
        total_inverse_loss += inverse_loss.item()
        total_consistency_loss += consistency_loss.item()
    return (total_loss / len(dataloader), total_recon_loss / len(dataloader),
            total_forward_loss / len(dataloader), total_inverse_loss / len(dataloader),
            total_consistency_loss / len(dataloader))

def validate_model(model, dataloader):
    model.eval()
    total_loss = 0
    total_recon_loss = 0
    total_forward_loss = 0
    total_inverse_loss = 0
    total_consistency_loss = 0
    with torch.no_grad():
        for states, actions, next_states in dataloader:
            loss, recon_loss, forward_loss, inverse_loss, consistency_loss = compute_upn_loss(model, states, actions, next_states)
            total_loss += loss.item()
            total_recon_loss += recon_loss.item()
            total_forward_loss += forward_loss.item()
            total_inverse_loss += inverse_loss.item()
            total_consistency_loss += consistency_loss.item()
    return (total_loss / len(dataloader), total_recon_loss / len(dataloader),
            total_forward_loss / len(dataloader), total_inverse_loss / len(dataloader),
            total_consistency_loss / len(dataloader))

def plot_losses(train_losses, val_losses):
    plt.figure(figsize=(15, 10))
    loss_types = ['Total', 'Reconstruction', 'Forward', 'Inverse', 'Consistency']
    for i, loss_type in enumerate(loss_types):
        plt.subplot(2, 3, i+1)
        plt.plot([losses[i] for losses in train_losses], label='Train')
        plt.plot([losses[i] for losses in val_losses], label='Validation')
        plt.title(f'{loss_type} Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
    plt.tight_layout()
    plt.savefig('supervised_upn_learning_losses.png')
    plt.show()

def main():
    states, actions, next_states = load_data()
    
    # Print shapes for debugging
    print(f"States shape: {states.shape}")
    print(f"Actions shape: {actions.shape}")
    print(f"Next states shape: {next_states.shape}")
    
    # Split data into training and validation sets
    split = int(0.8 * len(states))
    train_states, train_actions, train_next_states = states[:split], actions[:split], next_states[:split]
    val_states, val_actions, val_next_states = states[split:], actions[split:], next_states[split:]

    train_dataset = TensorDataset(train_states, train_actions, train_next_states)
    val_dataset = TensorDataset(val_states, val_actions, val_next_states)

    train_dataloader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_dataloader = DataLoader(val_dataset, batch_size=args.batch_size)

    # debug 1 by 1, trace from error back to where you think might be wrong,
    # then check what is passed in, does it match your expectation
    state_dim = states.shape[-1]
    action_dim = actions.shape[-1]

    print(f"State dimension: {state_dim}")
    print(f"Action dimension: {action_dim}")

    model = UPN(state_dim, action_dim, args.latent_size).to(device)
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)

    train_losses = []
    val_losses = []

    for epoch in range(args.num_epochs):
        train_loss = train_model(model, train_dataloader, optimizer)
        val_loss = validate_model(model, val_dataloader)
        
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        
        print(f"Epoch {epoch+1}/{args.num_epochs}")
        print(f"Train - Total: {train_loss[0]:.4f}, Recon: {train_loss[1]:.4f}, Forward: {train_loss[2]:.4f}, Inverse: {train_loss[3]:.4f}, Consistency: {train_loss[4]:.4f}")
        print(f"Val   - Total: {val_loss[0]:.4f}, Recon: {val_loss[1]:.4f}, Forward: {val_loss[2]:.4f}, Inverse: {val_loss[3]:.4f}, Consistency: {val_loss[4]:.4f}")

    plot_losses(train_losses, val_losses)

    # Save the model
    save_dir = os.path.join(os.getcwd(), 'mvp', 'params')
    os.makedirs(save_dir, exist_ok=True)
    model_filename = "supervised_upn_rnn.pth"
    model_path = os.path.join(save_dir, model_filename)
    torch.save(model.state_dict(), model_path)
    print(f"Model saved at: {model_path}")

if __name__ == "__main__":
    main()