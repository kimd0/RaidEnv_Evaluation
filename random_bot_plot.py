import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Argument parser setup
parser = argparse.ArgumentParser(description='Plot some data.')
parser.add_argument('--path', type=str, default="Z:\wonsang\gstar\GStarRandomSample", required=True)
parser.add_argument('--save_path', type=str, default="Z:\wonsang\gstar\new_plt", required=True)


def plot():
    args = parser.parse_args()
    logs = [
        "generate-0-0-healthmax",
        "generate-0-0-armor",
        "generate-0-0-movespeed",
        "generate-0-0-range",
        "generate-0-0-cooltime",
        "generate-0-0-casttime",
        "generate-0-0-damage",
        "generate-0-1-range",
        "generate-0-1-cooltime",
        "generate-0-1-casttime",
        "generate-0-1-damage",

        "generate-1-0-healthmax",
        "generate-1-0-armor",
        "generate-1-0-movespeed",
        "generate-1-0-range",
        "generate-1-0-cooltime",
        "generate-1-0-casttime",
        "generate-1-0-damage",
        "generate-1-1-range",
        "generate-1-1-cooltime",
        "generate-1-1-casttime",
        "generate-1-1-damage",

        "generate-2-0-healthmax",
        "generate-2-0-armor",
        "generate-2-0-movespeed",
        "generate-2-0-range",
        "generate-2-0-cooltime",
        "generate-2-0-casttime",
        "generate-2-0-damage",
        "generate-2-1-range",
        "generate-2-1-cooltime",
        "generate-2-1-casttime",
        "generate-2-1-damage",

        "generate-3-0-healthmax",
        "generate-3-0-armor",
        "generate-3-0-movespeed",
        "generate-3-0-range",
        "generate-3-0-cooltime",
        "generate-3-0-casttime",
        "generate-3-0-damage",
        "generate-3-1-range",
        "generate-3-1-cooltime",
        "generate-3-1-casttime",
        "generate-3-1-damage",
    ]

    datas = [
        "State.Agent0.Property.Health.Max",
        "State.Agent0.Property.Armor",
        "State.Agent0.Property.MoveSpeed",
        "State.Agent0.Skill0.Attack.Range",
        "State.Agent0.Skill0.Attack.Cooltime",
        "State.Agent0.Skill0.Attack.Casttime",
        "State.Agent0.Skill0.Attack.Amount",
        "State.Agent0.Skill1.Attack.Range",
        "State.Agent0.Skill1.Attack.Cooltime",
        "State.Agent0.Skill1.Attack.Casttime",
        "State.Agent0.Skill1.Attack.Amount",

        "State.Agent1.Property.Health.Max",
        "State.Agent1.Property.Armor",
        "State.Agent1.Property.MoveSpeed",
        "State.Agent1.Skill0.Heal.Range",
        "State.Agent1.Skill0.Heal.Cooltime",
        "State.Agent1.Skill0.Heal.Casttime",
        "State.Agent1.Skill0.Heal.Amount",
        "State.Agent1.Skill1.Shield.Range",
        "State.Agent1.Skill1.Shield.Cooltime",
        "State.Agent1.Skill1.Shield.Casttime",
        "State.Agent1.Skill1.Shield.Amount",

        "State.Agent2.Property.Health.Max",
        "State.Agent2.Property.Armor",
        "State.Agent2.Property.MoveSpeed",
        "State.Agent2.Skill0.Attack.Range",
        "State.Agent2.Skill0.Attack.Cooltime",
        "State.Agent2.Skill0.Attack.Casttime",
        "State.Agent2.Skill0.Attack.Amount",
        "State.Agent2.Skill1.Attack.Range",
        "State.Agent2.Skill1.Attack.Cooltime",
        "State.Agent2.Skill1.Attack.Casttime",
        "State.Agent2.Skill1.Attack.Amount",

        "State.Agent3.Property.Health.Max",
        "State.Agent3.Property.Armor",
        "State.Agent3.Property.MoveSpeed",
        "State.Agent3.Skill0.Attack.Range",
        "State.Agent3.Skill0.Attack.Cooltime",
        "State.Agent3.Skill0.Attack.Casttime",
        "State.Agent3.Skill0.Attack.Amount",
        "State.Agent3.Skill1.Attack.Range",
        "State.Agent3.Skill1.Attack.Cooltime",
        "State.Agent3.Skill1.Attack.Casttime",
        "State.Agent3.Skill1.Attack.Amount",
    ]
    for log, data in zip(logs, datas):
        # join path
        path = os.path.join(args.path, log)

        # List all csv files in the directory
        csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]

        agent_number = log.split('-')[1]
        skill_number = log.split('-')[2]

        if agent_number == str(1):
            if skill_number == str(0):
                y_columns = [
                    'Playtesting.WinRate',
                    f'Playtesting.Agent{agent_number}.EpisodeLength',
                    f'Playtesting.Agent{agent_number}.Heal.Dealt.PerSecond',
                    f'Playtesting.Agent{agent_number}.Damage.Taken'
                ]
            else:
                y_columns = [
                    'Playtesting.WinRate',
                    f'Playtesting.Agent{agent_number}.EpisodeLength',
                    f'Playtesting.Agent{agent_number}.Shield.Dealt.PerSecond',
                    f'Playtesting.Agent{agent_number}.Damage.Taken'
                ]
        else:
            # Y-axis columns
            y_columns = [
                'Playtesting.WinRate',
                f'Playtesting.Agent{agent_number}.EpisodeLength',
                f'Playtesting.Agent{agent_number}.Damage.Dealt',
                f'Playtesting.Agent{agent_number}.Damage.Taken'
            ]

        # X-axis column from the arguments
        x_col = data

        # Initialize an empty DataFrame to accumulate all data
        all_data = pd.DataFrame()

        # Read each csv file and concatenate the data
        for csv_file in csv_files:
            file_path = os.path.join(path, csv_file)
            df = pd.read_csv(file_path)
            all_data = pd.concat([all_data, df], ignore_index=True)

        # save_path
        save_path = os.path.join(args.save_path, f'{log}_scatter_plots.jpg')
        os.makedirs(args.save_path, exist_ok=True)

        # Set seaborn style for better visual appearance
        sns.set(style="darkgrid")

        # Create subplots for 4 scatter plots
        fig, axs = plt.subplots(2, 2, figsize=(15, 10))

        # Flatten the axes array for easy indexing
        axs = axs.flatten()

        # Plotting the data with seaborn scatterplot
        for i, y_col in enumerate(y_columns):
            if y_col in all_data.columns and x_col in all_data.columns:
                sns.scatterplot(x=x_col, y=y_col, data=all_data, ax=axs[i])

                # Labeling and titling each subplot
                axs[i].set_xlabel(x_col)
                axs[i].set_ylabel(y_col)
                axs[i].set_title(f'{y_col} vs {x_col}')

                # Rotate x-axis labels for better readability
                axs[i].tick_params(axis='x', rotation=45)

        # Adjust layout for better spacing
        plt.tight_layout()

        # Save the plot as a jpg file
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()


if __name__ == '__main__':
    plot()
