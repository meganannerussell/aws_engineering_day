# Smart Text Analytics for Open-Ended Responses

## The Challenge

When customers ask **custom open-ended questions**, our current system only shows a **word cloud** (word frequency counts). Not very insightful. Many customers even copy/paste results into ChatGPT - and still don't get the clarity they want.

We want to change that, unlocking the maximum value from our unstructured open-ended data.

## The Problem

Build a smarter way to:

1. **Group** responses into themes/topics
2. **Label & summarise** those themes in plain language
3. Add **sentiment analysis** for extra insight
4. **Output results** in a usable way (e.g. chart-ready, exportable)
5. Make it **quick, scalable, and cost-efficient**

**What about current AutoCoding?** Our new Autocoding 2.0 in QR uses fixed codeframes predefined per question/category - not suitable for custom questions. First prize would be creating output similar to Autocoding 2.0, but for unstructured questions.

## The Data

- **100–4,000 open-ended responses** per project
- **Responses:** a few sentences each
- **~1,000 projects per month**
- **Processing:** asynchronous (minutes is fine, no need for real-time)
- **Integration:** needs to plug into our charting framework
- **Sample datasets:** 6 datasets on various topics available in S3 bucket

*Note: These datasets are NOT sourced from client data, so no sensitive content - safe to share with AWS.*

## Getting Started

**Step 1: Explore the Data**

- Explore to the S3 bucket and examine the 6 sample datasets
- Understand the variety of topics, response lengths, and styles
- Get a feel for what "good" vs "noisy" responses look like

**Step 2: Play with AWS Tools**

- Start experimenting with available models
- Try basic clustering approaches on one small dataset
- See what challenges emerge naturally as you work

**Step 3: Iterate and Learn**

- Don't aim for perfection on day one
- Document what works, what doesn't, and why
- Focus on the core workflow: responses → topics → labels → insights

## 🧠 Pointers and Other Things to Explore

### The Problem is Actually Two Problems

Remember you're solving both:

- **Problem 1:** Mapping topics to verbatims
- **Problem 2:** Creating a survey-specific codeframe

There's a **harmonisation challenge** at scale - similar topic names representing the same thing make numerical reporting much harder.

### Architectural Approaches Worth Exploring

**Two-Stage Clustering + Labeling**

- Have you thought about using embeddings and clustering to group similar verbatims first, then creating topic labels for those groups?
- **Challenge to solve:** A verbatim can have multiple topics - most clustering algorithms assign a single cluster per data point
- **Pointer:** The grouping might just be codeframe creation - doesn't need to do everything. Then you could use something similar to the current AC2 approach to map verbatims to this harmonised topic list

**Topic Harmonisation Pipeline**

- Have you considered a second stage for harmonising initially produced topics?
- Second step groups **topics themselves** and renames them into harmonised labels

**LLM Chain with Memory**

- Have you considered chaining LLM calls with "memory" of topics already created?
- Build topic consistency as you process the dataset

### What Makes a "Good Topic" Label?

Think about these constraints:

- **Length:** 2, maybe 3 words maximum
- **Sentiment baked in or separate?**
    - "Great music" and "Bad music" vs "Music" with separate sentiment scores
    - Which approach works better for reporting?
- **Consistent granularity** is tricky - some topics naturally have more detail than others
- **The ultimate test:** "Will this look stupid on a quick report?"

### Error Handling & Model Refusals

**The failure mode to avoid:** One problematic verbatim causes the whole batch to fail = terrible user experience

**Things to think through:**

- What happens if one verbatim is absolutely vile and the model refuses to process it?
- How granular should processing be to minimise blast radius?
- How do you gracefully handle and report processing failures?
- What's your fallback strategy when models misbehave?

### Scale & Cost Considerations

**Processing volumes:** 1,000 projects/month × up to 4,000 responses = potentially 4M monthly responses

- Which AWS services make sense at this scale?
- How do you balance speed, cost, and accuracy?
- Async processing gives you flexibility - how do you use it?
- Don’t just use the biggest model you can - small cheap models can do many simple tasks. And remember you can mix and match models in the pipeline.

### Integration & Output Format

**Platform considerations:**

- What does our charting framework expect as input?
- How should this integrate with existing Quick Reports?
- What export formats would be most valuable?
- How do you make results immediately actionable for customers?

## Judging Criteria

Your solution will be judged on:

- **Insightfulness** – Do the outputs surface the *right* insights while ignoring noise?
- **Speed** – How quickly can it process a project?
- **Cost** – Is it efficient enough for production use?
- **Scalability** – Could it handle real-world data volumes?
- **Vibes** – Any fun extras? :185:

## Optional Extensions

**Platform Integration:**

- How will results be presented on the platform?
- How might this hook into charting or visualisation?
- How might this look in a Quick Report or current charts?
- What export formats would be most useful?

**Advanced Features:**

- Multi-language support
- Comparative analysis across time periods
- Integration with existing Autocoding 2.0 workflows
- Real-time processing capabilities