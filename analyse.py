import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import glob
import os

plt.close('all')

joined_files = os.path.join("./experiment_data/", "*.csv")
joined_list = glob.glob(joined_files)
df = pd.concat(map(pd.read_csv, joined_list), ignore_index=True)

# adding column if identified emotion is correct
df['Correct'] = 0
df.loc[df['True emotion'] == df['Response emotion'], 'Correct'] = 100

#==============================================
# ACCURACY FOR AUDIO vs WITHOUT AUDIO
# group by audio presence
dfGrSub = df[['Audio', 'Subject Name', 'Correct']].groupby(['Audio', 'Subject Name']).mean()
plotdf = pd.DataFrame({
    'Without Audio': dfGrSub.loc[0]['Correct'], 
    'With Audio': dfGrSub.loc[1]['Correct']
})
# print(plotdf)
# plot for mean for both cases with standard deviation
fig1, ax1 = plt.subplots(1, 1)
plotdf.mean().plot.bar(
    ax=ax1, 
    yerr=plotdf.std(), 
    rot=0, 
    capsize=4, 
    legend=False, 
    xlabel='Audio status', 
    ylabel='Accuracy (%)', 
    title='Overall accuracy across subjects\nwith audio and without audio'
)
ax1.grid()
adt = plotdf['With Audio']
adf = plotdf['Without Audio']
print("Homegeneity test on only audio category: {}".format(stats.levene(adt, adf)))
print("Normality test on only audio category: {}, {}".format(stats.shapiro(adt), stats.shapiro(adf)))
print("T-Test result on only audio category: {}".format(stats.wilcoxon(adt, adf)))


#==============================================
# ACCURACY FOR DIFFERENT EMOTIONS FOR AUDIO vs WITHOUT AUDIO
# group by each emotion, audio
dfGrEm = df[['True emotion', 'Audio', 'Subject Name', 'Correct']].groupby(['True emotion', 'Audio', 'Subject Name']).mean()
dfGrEm = dfGrEm.reset_index(['Audio', 'Subject Name'])
af = dfGrEm[dfGrEm['Audio']==False]
at = dfGrEm[dfGrEm['Audio']==True]
plotdfE = pd.DataFrame({
    'Without Audio': af['Correct'],
    'With Audio': at['Correct']
})
plotdfE = plotdfE.groupby(['True emotion'])
# plot for mean for both cases for each emotion with standard deviation
fig2, ax2 = plt.subplots(1, 1)
plotdfE.mean().plot.bar(
    ax=ax2, 
    yerr=plotdfE.std(), 
    rot=0, 
    capsize=4, 
    xlabel='Emotions', 
    ylabel='Accuracy (%)', 
    title='Accuracy for different emotions across subjects\nwith audio and without audio'
)
ax2.grid()


#==============================================
# ACCURACY FOR DIFFERENT SPEAKER GENDERS FOR AUDIO vs WITHOUT AUDIO
# group by each speaker gender, audio
dfGrSpG = df[['Speaker gender', 'Audio', 'Subject Name', 'Correct']].groupby(['Speaker gender', 'Audio', 'Subject Name']).mean()
dfGrSpG = dfGrSpG.reset_index(['Audio', 'Subject Name'])
af = dfGrSpG[dfGrSpG['Audio']==False]
at = dfGrSpG[dfGrSpG['Audio']==True]
plotdfSpG = pd.DataFrame({
    'Without Audio': af['Correct'],
    'With Audio': at['Correct']
})
plotdfSpG = plotdfSpG.groupby(['Speaker gender'])
# plot for mean for both cases for each speaker gender with standard deviation
fig3, ax3 = plt.subplots(1, 1)
plotdfSpG.mean().plot.bar(
    ax=ax3, 
    yerr=plotdfSpG.std(), 
    rot=0, 
    capsize=4, 
    xlabel='Speaker genders', 
    ylabel='Accuracy (%)', 
    title='Accuracy for different speaker genders across subjects\nwith audio and without audio'
)
ax3.grid()


#==============================================
# ACCURACY FOR DIFFERENT SUBJECT GENDERS FOR AUDIO vs WITHOUT AUDIO
# group by each subject gender, audio
dfGrSbG = df[['Subject gender', 'Audio', 'Subject Name', 'Correct']].groupby(['Subject gender', 'Audio', 'Subject Name']).mean()
dfGrSbG = dfGrSbG.reset_index(['Audio', 'Subject Name'])
af = dfGrSbG[dfGrSbG['Audio']==False]
at = dfGrSbG[dfGrSbG['Audio']==True]
plotdfSbG = pd.DataFrame({
    'Without Audio': af['Correct'],
    'With Audio': at['Correct']
})
plotdfSbG = plotdfSbG.groupby(['Subject gender'])
# plot for mean for both cases for each subject gender with standard deviation
fig4, ax4 = plt.subplots(1, 1)
plotdfSbG.mean().plot.bar(
    ax=ax4, 
    yerr=plotdfSbG.std(), 
    rot=0, 
    capsize=4, 
    xlabel='Subject genders', 
    ylabel='Accuracy (%)', 
    title='Accuracy for different subject genders across subjects\nwith audio and without audio'
)
ax4.grid()

plt.show()