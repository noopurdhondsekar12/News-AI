# News AI Scheduler Run Policy

## Overview
The News AI Scheduler manages automated news processing jobs across multiple categories with different priorities and frequencies. It uses APScheduler for job scheduling and submits processing requests to a background queue for asynchronous execution.

## Categories and Frequencies

### Live News
- **Frequency**: Every 15 minutes
- **Sources**: BBC, Reuters, NYT, Al Jazeera, The Guardian
- **Priority**: 10 (Highest)
- **Options**: Urgent voice, breaking news avatar, live channel

### Finance News
- **Frequency**: Every hour
- **Sources**: Bloomberg, WSJ, FT, CNBC, MarketWatch
- **Priority**: 7
- **Options**: Professional voice, business avatar, finance channel

### World News
- **Frequency**: Every 6 hours
- **Sources**: BBC World, Reuters World, Al Jazeera News, DW
- **Priority**: 5
- **Options**: Neutral voice, global avatar, world channel

### Regional News
- **Frequency**: Every 6 hours
- **Sources**: The Hindu, Indian Express, NDTV, Times of India
- **Priority**: 3
- **Options**: Conversational voice, local avatar, regional channel

### Kids News
- **Frequency**: Every 6 hours
- **Sources**: Scholastic, Time for Kids, National Geographic Kids, BBC Newsround
- **Priority**: 1 (Lowest)
- **Options**: Friendly voice, fun avatar, kids channel, audio disabled

## Scheduling Behavior

### Job Staggering
- Jobs within each category are staggered by 2 minutes to prevent system overload
- Live category jobs are distributed across the 15-minute interval
- Other categories stagger hourly or 6-hourly runs

### Queue Submission
- All scheduled jobs submit to the background queue instead of processing directly
- This ensures non-blocking operation and allows for load balancing
- Jobs are prioritized based on category importance

### Error Handling
- Failed jobs are logged and counted in scheduler statistics
- Scheduler continues running despite individual job failures
- Misfire grace time: 30 seconds

### Concurrency Control
- Max instances per job: 1 (prevents duplicate processing)
- Max concurrent jobs: 3 (configured in scheduler defaults)
- Coalesce: True (combines missed runs)

## Manual Triggers
The scheduler supports manual trigger endpoints for testing and immediate processing:
- Trigger specific source in category
- Trigger all sources in category
- Trigger one source from each category

## Monitoring
Scheduler provides real-time statistics:
- Jobs scheduled, completed, failed
- Last run timestamp
- Next run times for all jobs
- Current running status

## Configuration
All scheduling parameters are configurable through the `news_sources` dictionary in the scheduler class. Timezone is set to UTC for consistent global operation.