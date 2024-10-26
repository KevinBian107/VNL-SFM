## Research Question & Progress

### Context:
The cerebellum have been long theorized to play an crucial rule in motor control and learning (Forward modeling). Corollary discharge encodes a efferent copy of the motor command to be processed to predict the consequences of actions before sensory feedback is available. Such process would help us predicts how the sensory state of our body will change and how should these actions be performed, achieving better performances in control.

Using examples from (Albert and Shadmehr, 2018), with the starting and ending positions in hand, the parietal regions of your cerebral cortex compute the path of the arm that connects these positions in space the trajectory of the movement. After the trajectory is determined, your primary motor cortex and other associated pre-motor areas then carefully transform this sensory signal into a motor plan, namely the patterns of muscle contraction that will move your arm along the desired path towards the coffee.

### Questions:
Does establishing a Forward Model, similar to the Cerebellum's function, facilitate motor action execution by providing a motor plan derived from previous motor control experiences for additional guidance (compare to pure sensory feedback like in model-free RL)? Moreover, can this new motor learning process be incorporated into the GDP for future motor controls?

- Objective 1: See if such biologically inspired strategy (for example, maybe using mechanistic insight, maybe using neuronal representation as inductive biases) improves performance;
- Objective 2: See if the Forward Model would resemble functionality and behavior of the cerebellum (for example, showing gradual learning of new motor skills).
  - Idealy using a more biological realistic model with more biological realistic task such as the rodent model in VNL.


## SFM-PPO Control Examples
<div style="width: 100%; padding: 5px; display: flex; justify-content: center; gap: 20px;">
          <div style="width: 30%; display: flex; flex-direction: column; align-items: center;">
            <video controls autoplay style="width: 100%; height: auto;" muted>
              <source src="../VNL-SFM/demos/website/demo1.mp4" type="video/mp4">
              Your browser does not support the video tag.
            </video>
            <blockquote>Deep-RL Inverted Pendulum agent trained using Fm-PPO</blockquote>
          </div>
          <div style="width: 30%; display: flex; flex-direction: column; align-items: center;">
            <video controls autoplay style="width: 100%; height: auto;" muted>
              <source src="../VNL-SFM/demos/website/sfmppo_converge_712.mp4" type="video/mp4">
              Your browser does not support the video tag.
            </video>
            <blockquote>Deep-RL Half Cheetah agent trained using SFm-PPO</blockquote>
          </div>
        <div style="width: 30%; display: flex; flex-direction: column; align-items: center;">
            <video controls autoplay style="width: 100%; height: auto;" muted>
              <source src="../VNL-SFM/demos/website/ppo_5e6_nice.mp4" type="video/mp4">
              Your browser does not support the video tag.
            </video>
            <blockquote>Deep-RL Half Cheetah agent trained using PPO</blockquote>
        </div>
</div>

<!-- <div style="width: 100%; display: flex; flex-direction: column; align-items: center;">
              <video controls autoplay style="width: 100%; height: auto;" muted>
                <source src="../VNL-SFM/demos/website/acti_ppo.mp4" type="video/mp4">
                Your browser does not support the video tag.
              </video>
              <blockquote>Deep-RL Half Cheetah agent trained using PPO Action Space & Action Activation PCA</blockquote>
          </div> -->

<!-- <div style="width: 100%; display: flex; flex-direction: column; align-items: center;">
              <video controls autoplay style="width: 100%; height: auto;" muted>
                <source src="../VNL-SFM/demos/website/acti_sfmppo_kl.mp4" type="video/mp4">
                Your browser does not support the video tag.
              </video>
              <blockquote>Deep-RL Half Cheetah agent trained using SFMPPO Latent Space & Action Activation PCA</blockquote>
          </div>

<div style="width: 100%; display: flex; flex-direction: column; align-items: center;">
              <video controls autoplay style="width: 100%; height: auto;" muted>
                <source src="../VNL-SFM/demos/website/sfmppo_full.mp4" type="video/mp4">
                Your browser does not support the video tag.
              </video>
              <blockquote>Deep-RL Half Cheetah agent trained using SFMPPO Full PCA</blockquote>
          </div> -->

## Schematic:

![Alt text](demos/website/dynamics_model.png)