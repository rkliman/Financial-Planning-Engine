import textwrap
import matplotlib.pyplot as plt
import seaborn as sns
import json

def wrap_labels(ax, width, break_long_words=False):
    labels = []
    for label in ax.get_xticklabels():
        text = label.get_text()
        labels.append(textwrap.fill(text, width=width,
                      break_long_words=break_long_words))
    ax.set_xticklabels(labels, rotation=0)

    labels = []
    for label in ax.get_yticklabels():
        text = label.get_text()
        labels.append(textwrap.fill(text, width=width,
                      break_long_words=break_long_words))
    ax.set_yticklabels(labels, rotation=0)

def plot_finances(df_principal_t, df_contribution_t, constants):
    W, Wt, T1, T2, R, I, SP, NG = constants

    # -------------------
    # Heatmap 1: Required Principal
    # -------------------
    fig1, ax1 = plt.subplots(figsize=(8.5, 3))
    df_principal_fmt = df_principal_t.applymap(lambda x: f"${x:,.0f}")
    sns.heatmap(df_principal_t, annot=df_principal_fmt, fmt="", cmap="OrRd", ax=ax1,
                cbar_kws={'label': 'Principal ($)'})
    ax1.set_title("Required Principal by Financial Goal")
    # ax1.set_xlabel("Financial Goal")
    ax1.set_ylabel("Account Type")
    ax1.tick_params(axis='x', labelsize=10, labelbottom=False,
                    bottom=False, labeltop=True, top=False)
    ax1.tick_params(axis='y', labelsize=10)
    wrap_labels(ax1, 15, break_long_words=True)
    fig1.tight_layout()
    fig1.savefig("figs/required_principal.png", dpi=300)
    plt.close(fig1)

    # -------------------
    # Heatmap 2: Yearly Contribution
    # -------------------
    fig2, ax2 = plt.subplots(figsize=(8.5, 3))
    df_contribution_fmt = df_contribution_t.applymap(
        lambda x: f"${x:,.0f} ({x/Wt:.1%})")
    sns.heatmap(df_contribution_t, annot=df_contribution_fmt, fmt="", cmap="OrRd", ax=ax2,
                cbar_kws={'label': 'Contribution ($/yr)'})
    ax2.set_title("Yearly Contribution by Financial Goal")
    # ax2.set_xlabel("Financial Goal")
    ax2.set_ylabel("Account Type")
    ax2.tick_params(axis='x', labelsize=10, labelbottom=False,
                    bottom=False, labeltop=True, top=False)
    ax2.tick_params(axis='y', labelsize=10)
    wrap_labels(ax2, 15, break_long_words=True)
    fig2.tight_layout()
    fig2.savefig("figs/yearly_contribution.png", dpi=300)
    plt.close(fig2)

    # -------------------
    # Typst Document
    # -------------------
    info_dict = {
        "pre_tax": W,
        "post_tax": Wt,
        "retirement": Wt,
        "invest_period": T1,
        "retire_period": T2,
        "expected_return": R*100,
        "inflation_rate": I*100,
        "financial_goals": {
            "supplemented": (1-SP)*100,
            "sustainable_retirement": 100,
            "generational_wealth": 100,
            "nobility": NG*100
        }
    }
    
    json.dump(info_dict, open("info.json", "w"), indent=4)

    # Optionally compile Typst to PDF
    try:
        import subprocess
        subprocess.run(["typst", "compile", "retirement_report.typ", "retirement_report.pdf"], check=True)
    except FileNotFoundError:
        print("Typst not found. Skipping PDF compilation.")
    except Exception as e:
        print(f"Error running Typst: {e}")
