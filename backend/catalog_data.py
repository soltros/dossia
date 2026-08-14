"""
Curated Discover Catalog for Dossia
Contains 110 high-signal, independent publications across 11 categories.
"""

CURATED_LINUX = [
    {
        "id": "phoronix",
        "name": "Phoronix",
        "site_url": "https://www.phoronix.com/",
        "feed_url": "https://www.phoronix.com/rss.php",
        "category": "Linux & Kernel",
        "best_for": "Hardware benchmarks, GPU/Vulkan drivers, and low-level Linux performance.",
        "why_read": "Michael Larabel tracks patch submissions, GPU/Vulkan drivers, kernel optimization work, and automated benchmarks.",
        "enabled": 1
    },
    {
        "id": "lwn",
        "name": "LWN.net (Linux Weekly News)",
        "site_url": "https://lwn.net/",
        "feed_url": "https://lwn.net/headlines/rss",
        "category": "Linux & Kernel",
        "best_for": "Deep, technical journalism on kernel architecture and developer mailing lists.",
        "why_read": "Premier publication covering architectural decisions, security patches, and maintainer debates inside the Linux kernel.",
        "enabled": 1
    },
    {
        "id": "itsfoss",
        "name": "It's FOSS",
        "site_url": "https://itsfoss.com/",
        "feed_url": "https://itsfoss.com/rss/",
        "category": "Linux & Kernel",
        "best_for": "General desktop Linux news, open-source project spotlights, and guides.",
        "why_read": "Covers daily news around major desktop environments, newly released open-source utilities, and distro updates.",
        "enabled": 1
    },
    {
        "id": "9to5linux",
        "name": "9to5Linux",
        "site_url": "https://9to5linux.com/",
        "feed_url": "https://9to5linux.com/feed",
        "category": "Linux & Kernel",
        "best_for": "Fast-paced distribution releases, kernel version drops, and software updates.",
        "why_read": "Quick turnaround on new release announcements for popular distros (Fedora, Arch, Debian, Ubuntu) and desktop environments.",
        "enabled": 1
    },
    {
        "id": "omgubuntu",
        "name": "OMG! Ubuntu!",
        "site_url": "https://www.omgubuntu.co.uk/",
        "feed_url": "https://www.omgubuntu.co.uk/feed",
        "category": "Linux & Kernel",
        "best_for": "Ubuntu ecosystem, GNOME developments, and desktop app updates.",
        "why_read": "Joey Sneddon covers cross-distro desktop topics, GTK/GNOME app updates, and Linux ecosystem news.",
        "enabled": 1
    },
    {
        "id": "gamingonlinux",
        "name": "GamingOnLinux",
        "site_url": "https://www.gamingonlinux.com/",
        "feed_url": "https://www.gamingonlinux.com/article_rss.php",
        "category": "Linux & Kernel",
        "best_for": "Proton/Wine compatibility, Steam on Linux, native game releases, and Mesa/Vulkan progress.",
        "why_read": "Liam Dawe covers the rapid pace of Linux gaming, graphics driver progress (Mesa/Vulkan), and portable PC gaming ecosystems.",
        "enabled": 1
    },
    {
        "id": "distrowatch",
        "name": "DistroWatch Weekly",
        "site_url": "https://distrowatch.com/",
        "feed_url": "https://distrowatch.com/news/dww.xml",
        "category": "Linux & Kernel",
        "best_for": "Tracking all active distributions, package changes, and new project releases.",
        "why_read": "Summarizes major ecosystem announcements, release schedules, package migrations, and community reviews.",
        "enabled": 1
    },
    {
        "id": "nixcraft",
        "name": "nixCraft",
        "site_url": "https://www.cyberciti.biz/",
        "feed_url": "https://www.cyberciti.biz/feed/",
        "category": "Linux & Kernel",
        "best_for": "System administrators, DevOps workflows, shell tips, and security alerts.",
        "why_read": "Vivek Gite focuses on practical sysadmin work, containerization, server security vulnerabilities, and command-line tooling.",
        "enabled": 1
    },
    {
        "id": "linuxtoday",
        "name": "Linux Today",
        "site_url": "https://www.linuxtoday.com/",
        "feed_url": "https://www.linuxtoday.com/feed/",
        "category": "Linux & Kernel",
        "best_for": "Daily curated news aggregation across the entire FOSS world.",
        "why_read": "Central feed pulling together security advisories, enterprise open-source news, tutorials, and distro release notes.",
        "enabled": 1
    },
    {
        "id": "linuxuprising",
        "name": "Linux Uprising",
        "site_url": "https://www.linuxuprising.com/",
        "feed_url": "https://feeds.feedburner.com/LinuxUprising",
        "category": "Linux & Kernel",
        "best_for": "App reviews, small utility discovery, command-line tweaks, and PPA/Flatpak highlights.",
        "why_read": "Great for discovering niche open-source utilities, terminal tools, and detailed installation recipes.",
        "enabled": 1
    }
]

CURATED_GAMING = [
    {
        "id": "rockpapershotgun",
        "name": "Rock Paper Shotgun",
        "site_url": "https://www.rockpapershotgun.com/",
        "feed_url": "https://www.rockpapershotgun.com/feed",
        "category": "Gaming & Reviews",
        "best_for": "PC gaming, niche genres, simulation, strategy, and indie deep dives.",
        "why_read": "Sharp, voice-driven editorial work spotlighting weird indie gems, complex RPGs, and patch impressions.",
        "enabled": 1
    },
    {
        "id": "eurogamer",
        "name": "Eurogamer & Digital Foundry",
        "site_url": "https://www.eurogamer.net/",
        "feed_url": "https://www.eurogamer.net/feed",
        "category": "Gaming & Reviews",
        "best_for": "Rigorous journalism, in-depth reviews, and hardware performance breakdowns.",
        "why_read": "Respected European outlet for balanced critique. Digital Foundry is the gold standard for graphics and frame-rate analysis.",
        "enabled": 1
    },
    {
        "id": "pcgamer",
        "name": "PC Gamer",
        "site_url": "https://www.pcgamer.com/",
        "feed_url": "https://www.pcgamer.com/rss/",
        "category": "Gaming & Reviews",
        "best_for": "Mainstream PC gaming news, modding, hardware coverage, and major updates.",
        "why_read": "Fast reporting on major studio releases, hardware guides, patch breakdowns, and community mods.",
        "enabled": 1
    },
    {
        "id": "gamedeveloper",
        "name": "Game Developer",
        "site_url": "https://www.gamedeveloper.com/",
        "feed_url": "https://www.gamedeveloper.com/rss.xml",
        "category": "Gaming & Reviews",
        "best_for": "Behind-the-scenes engineering, game design theory, and industry postmortems.",
        "why_read": "Written for creators, focusing on game engines, narrative design, rendering tech, and development realities.",
        "enabled": 1
    },
    {
        "id": "gamesindustry",
        "name": "GamesIndustry.biz",
        "site_url": "https://www.gamesindustry.biz/",
        "feed_url": "https://www.gamesindustry.biz/feed",
        "category": "Gaming & Reviews",
        "best_for": "The business, economics, mergers, sales data, and labor trends in gaming.",
        "why_read": "Definitive trade publication for tracking market shifts, developer acquisitions, platform revenues, and corporate decisions.",
        "enabled": 1
    },
    {
        "id": "aftermath",
        "name": "Aftermath",
        "site_url": "https://aftermath.site/",
        "feed_url": "https://aftermath.site/feed",
        "category": "Gaming & Reviews",
        "best_for": "Independent games journalism, labor reporting, internet culture, and long-form essays.",
        "why_read": "Worker-owned cooperative free of corporate SEO incentives, focusing on honest reporting and cultural critique.",
        "enabled": 1
    },
    {
        "id": "nintendolife",
        "name": "Nintendo Life",
        "site_url": "https://www.nintendolife.com/",
        "feed_url": "https://www.nintendolife.com/feed",
        "category": "Gaming & Reviews",
        "best_for": "Dedicated coverage of Nintendo hardware, first-party releases, and eShop indies.",
        "why_read": "Premier hub for Nintendo tracking hardware news, firmware updates, retro features, and exclusives.",
        "enabled": 1
    },
    {
        "id": "gematsu",
        "name": "Gematsu",
        "site_url": "https://www.gematsu.com/",
        "feed_url": "https://www.gematsu.com/feed",
        "category": "Gaming & Reviews",
        "best_for": "Fast announcements, Japanese gaming news, RPGs, and release dates.",
        "why_read": "Direct feed for press releases, development milestones, translation announcements, and overseas reveals.",
        "enabled": 1
    },
    {
        "id": "polygon",
        "name": "Polygon",
        "site_url": "https://www.polygon.com/",
        "feed_url": "https://www.polygon.com/rss/index.xml",
        "category": "Gaming & Reviews",
        "best_for": "Narrative deep dives, cultural commentary, guides, and long-form essays.",
        "why_read": "Balances mainstream release coverage with well-researched features examining game histories and artistic direction.",
        "enabled": 1
    },
    {
        "id": "siliconera",
        "name": "Siliconera",
        "site_url": "https://www.siliconera.com/",
        "feed_url": "https://www.siliconera.com/feed/",
        "category": "Gaming & Reviews",
        "best_for": "International video game news, Japanese RPGs, localized indie releases, and developer interviews.",
        "why_read": "Reliable coverage on release dates, localization status, and overseas developer discussions.",
        "enabled": 1
    }
]

CURATED_LABOR = [
    {
        "id": "jacobin",
        "name": "Jacobin",
        "site_url": "https://jacobin.com/",
        "feed_url": "https://jacobin.com/feed",
        "category": "Labor & Politics",
        "best_for": "Explicit democratic socialist political analysis, electoral commentary, and international history.",
        "why_read": "Flagship publication of the modern American democratic socialist movement.",
        "enabled": 1
    },
    {
        "id": "inthesetimes",
        "name": "In These Times",
        "site_url": "https://inthesetimes.com/",
        "feed_url": "https://inthesetimes.com/rss",
        "category": "Labor & Politics",
        "best_for": "Labor investigative reporting, workplace organizing, and grassroots social movements.",
        "why_read": "Founded in 1976, dedicated to advancing economic justice, union campaigns, and working-class struggles.",
        "enabled": 1
    },
    {
        "id": "dissent",
        "name": "Dissent Magazine",
        "site_url": "https://www.dissentmagazine.org/",
        "feed_url": "https://www.dissentmagazine.org/feed/",
        "category": "Labor & Politics",
        "best_for": "Long-form intellectual debate, democratic left theory, cultural criticism, and policy analysis.",
        "why_read": "Rigorous long-form debates on political strategy, foreign policy, and democratic theory.",
        "enabled": 1
    },
    {
        "id": "labornotes",
        "name": "Labor Notes",
        "site_url": "https://labornotes.org/",
        "feed_url": "https://labornotes.org/feed",
        "category": "Labor & Politics",
        "best_for": "Rank-and-file union organizing, strike reporting, and workplace strategy.",
        "why_read": "Reporting directly from shop floors, union halls, and contract fights across the US.",
        "enabled": 1
    },
    {
        "id": "thelever",
        "name": "The Lever",
        "site_url": "https://www.levernews.com/",
        "feed_url": "https://www.levernews.com/rss/",
        "category": "Labor & Politics",
        "best_for": "Reader-supported investigative journalism on corporate lobbying, corruption, and money in politics.",
        "why_read": "Investigates corporate malfeasance, campaign finance corruption, and regulatory capture without ads.",
        "enabled": 1
    },
    {
        "id": "democraticleft",
        "name": "Democratic Left (DSA)",
        "site_url": "https://www.dsausa.org/democratic-left/",
        "feed_url": "https://www.dsausa.org/feed/",
        "category": "Labor & Politics",
        "best_for": "Internal socialist strategy, local chapter organizing, and official movement analysis.",
        "why_read": "Official publication of the Democratic Socialists of America covering local organizing drives and solidarity.",
        "enabled": 1
    },
    {
        "id": "therealnews",
        "name": "The Real News Network (TRNN)",
        "site_url": "https://therealnews.com/",
        "feed_url": "https://therealnews.com/feed",
        "category": "Labor & Politics",
        "best_for": "Video journalism, labor podcasts, racial and economic justice reporting.",
        "why_read": "Baltimore-based non-profit newsroom focused on frontline worker interviews and labor actions.",
        "enabled": 1
    },
    {
        "id": "currentaffairs",
        "name": "Current Affairs",
        "site_url": "https://www.currentaffairs.org/",
        "feed_url": "https://currentaffairs.substack.com/feed",
        "category": "Labor & Politics",
        "best_for": "Accessible political essays, media criticism, and witty socialist commentary.",
        "why_read": "Pairs colorful, readable design with rigorous breakdowns of neoliberal rhetoric and media framing.",
        "enabled": 1
    },
    {
        "id": "dollarsandsense",
        "name": "Dollars & Sense",
        "site_url": "https://www.dollarsandsense.org/",
        "feed_url": "https://www.dollarsandsense.org/latest/rss/",
        "category": "Labor & Politics",
        "best_for": "Popular economic education and left analysis of fiscal/monetary policy.",
        "why_read": "Edited by economists and journalists since 1974, demystifying inflation and trade agreements.",
        "enabled": 1
    },
    {
        "id": "dropsitenews",
        "name": "Drop Site News",
        "site_url": "https://www.dropsitenews.com/",
        "feed_url": "https://www.dropsitenews.com/feed",
        "category": "Labor & Politics",
        "best_for": "Investigative foreign policy, national security whistleblowing, and government transparency.",
        "why_read": "Founded by Ryan Grim and Jeremy Scahill for unfiltered reporting on US empire and defense contractors.",
        "enabled": 1
    }
]

CURATED_CULTURE = [
    {
        "id": "vulture",
        "name": "Vulture (New York Magazine)",
        "site_url": "https://www.vulture.com/",
        "feed_url": "https://feeds.feedburner.com/nymag/vulture",
        "category": "Culture & Criticism",
        "best_for": "Cultural criticism, television/film analysis, and smart pop culture journalism.",
        "why_read": "Deconstructs modern media tropes and industry trends with intellectual rigor and sharp humor.",
        "enabled": 1
    },
    {
        "id": "pucknews",
        "name": "Puck News (What I'm Hearing)",
        "site_url": "https://puck.news/",
        "feed_url": "https://puck.news/feed/",
        "category": "Culture & Criticism",
        "best_for": "Hard-nosed Hollywood business realities, executive infighting, and studio economics.",
        "why_read": "Matt Belloni focuses on streaming deficits, executive churn, litigation, and labor struggles.",
        "enabled": 1
    },
    {
        "id": "theankler",
        "name": "The Ankler",
        "site_url": "https://theankler.com/",
        "feed_url": "https://theankler.com/feed",
        "category": "Culture & Criticism",
        "best_for": "Unvarnished Hollywood insider reporting, labor realities, and media shakeups.",
        "why_read": "Skeptical trade reporting focused on union negotiations, executive missteps, and industry contraction.",
        "enabled": 1
    },
    {
        "id": "defector",
        "name": "Defector",
        "site_url": "https://defector.com/",
        "feed_url": "https://defector.com/feed/",
        "category": "Culture & Criticism",
        "best_for": "Worker-owned cultural commentary, media critiques, and anti-corporate essays.",
        "why_read": "Subscriber-owned cooperative featuring sharp pop-culture commentary and zero access journalism.",
        "enabled": 1
    },
    {
        "id": "avclub",
        "name": "The A.V. Club",
        "site_url": "https://www.avclub.com/",
        "feed_url": "https://www.avclub.com/rss",
        "category": "Culture & Criticism",
        "best_for": "Film and TV reviews, pop culture roundups, and media analysis.",
        "why_read": "Focuses on the art and cultural impact of film, television, and music without celebrity gossip.",
        "enabled": 1
    },
    {
        "id": "popula",
        "name": "Popula",
        "site_url": "https://popula.com/",
        "feed_url": "https://popula.com/feed/",
        "category": "Culture & Criticism",
        "best_for": "Alternative cultural essays, international perspectives, and media literacy.",
        "why_read": "Ad-free cooperative publication examining how wealth, power, and entertainment intersect.",
        "enabled": 1
    },
    {
        "id": "indiewire",
        "name": "IndieWire",
        "site_url": "https://www.indiewire.com/",
        "feed_url": "https://www.indiewire.com/feed/",
        "category": "Culture & Criticism",
        "best_for": "Independent filmmaking, festival circuits, and director/craft-focused reporting.",
        "why_read": "Prioritizes screenwriting, cinematography, and production mechanics over celebrity PR.",
        "enabled": 1
    },
    {
        "id": "thr_business",
        "name": "The Hollywood Reporter: Business & Labor",
        "site_url": "https://www.hollywoodreporter.com/c/business/",
        "feed_url": "https://www.hollywoodreporter.com/c/business/feed/",
        "category": "Culture & Criticism",
        "best_for": "Tracking strikes, union contracts (WGA, SAG-AFTRA, IATSE), and legal battles.",
        "why_read": "Essential reporting on working conditions of below-the-line crews and guild negotiations.",
        "enabled": 1
    },
    {
        "id": "laineygossip",
        "name": "Lainey Gossip",
        "site_url": "https://www.laineygossip.com/",
        "feed_url": "https://www.laineygossip.com/rss",
        "category": "Culture & Criticism",
        "best_for": "Deconstructing celebrity PR strategies, media manipulation, and fame culture.",
        "why_read": "Decodes Hollywood public relations, calculated paparazzi drops, and celebrity marketing moves.",
        "enabled": 1
    },
    {
        "id": "nofilmschool",
        "name": "No Film School",
        "site_url": "https://nofilmschool.com/",
        "feed_url": "https://nofilmschool.com/rss.xml",
        "category": "Culture & Criticism",
        "best_for": "Ground-level production reality, working-crew perspectives, and filmmaking economics.",
        "why_read": "Covers entertainment industry news from the perspective of the working class on set.",
        "enabled": 1
    }
]

CURATED_SELFHOSTING = [
    {
        "id": "selfhst",
        "name": "selfh.st",
        "site_url": "https://selfh.st/",
        "feed_url": "https://selfh.st/rss/",
        "category": "Self-Hosting & HomeLab",
        "best_for": "Weekly self-hosted app roundups, community spotlights, and software updates.",
        "why_read": "Ethan Sholly tracks newly open-sourced tools, self-hosted web apps, container projects, and homelab news.",
        "enabled": 1
    },
    {
        "id": "awesome_selfhosted",
        "name": "Awesome-Selfhosted",
        "site_url": "https://github.com/awesome-selfhosted/awesome-selfhosted",
        "feed_url": "https://github.com/awesome-selfhosted/awesome-selfhosted/commits/master.atom",
        "category": "Self-Hosting & HomeLab",
        "best_for": "The definitive directory of self-hostable network services and web applications.",
        "why_read": "Aggressively curated repository tracking active projects across every functional homelab category.",
        "enabled": 1
    },
    {
        "id": "servethehome",
        "name": "ServeTheHome (STH)",
        "site_url": "https://www.servethehome.com/",
        "feed_url": "https://www.servethehome.com/feed/",
        "category": "Self-Hosting & HomeLab",
        "best_for": "Enterprise-grade home server hardware, mini PCs, and high-speed networking.",
        "why_read": "Deep teardowns of rack servers, low-power clusters, NVMe fabrics, and second-hand enterprise gear.",
        "enabled": 1
    },
    {
        "id": "ibracorp",
        "name": "Ibracorp",
        "site_url": "https://ibracorp.io/",
        "feed_url": "https://ibracorp.io/feed/",
        "category": "Self-Hosting & HomeLab",
        "best_for": "Containerized homelab deployment architectures, Unraid/TrueNAS, Docker Compose, and reverse proxies.",
        "why_read": "Production-style recipes for setting up media stacks, Authentik SSO, WireGuard meshes, and hardened infrastructure.",
        "enabled": 1
    },
    {
        "id": "christian_lempa",
        "name": "Christian Lempa",
        "site_url": "https://christianlempa.com/",
        "feed_url": "https://christianlempa.com/index.xml",
        "category": "Self-Hosting & HomeLab",
        "best_for": "Infrastructure-as-code, GitOps, Proxmox VE, and enterprise architecture scaled for homes.",
        "why_read": "Modern DevOps practices applied to personal infrastructure—automating with Terraform, Ansible, and Kubernetes.",
        "enabled": 1
    },
    {
        "id": "linuxserver_io",
        "name": "LinuxServer.io Blog",
        "site_url": "https://www.linuxserver.io/blog",
        "feed_url": "https://github.com/linuxserver/docker-templates/commits/master.atom",
        "category": "Self-Hosting & HomeLab",
        "best_for": "Container maintenance, base image design, and Docker fleet optimization.",
        "why_read": "Updates on container security, multi-arch builds, and upstream changes from the premier container team.",
        "enabled": 1
    },
    {
        "id": "kinkead_tech",
        "name": "Kinkead Tech",
        "site_url": "https://kinkeadtech.com/",
        "feed_url": "https://kinkeadtech.com/feed/",
        "category": "Self-Hosting & HomeLab",
        "best_for": "Step-by-step guides for media automation, Usenet/torrent clients, and home storage setups.",
        "why_read": "Practical walkthroughs for setting up automated media pipelines, storage pools, and VPN tunnels.",
        "enabled": 1
    },
    {
        "id": "danie_me",
        "name": "Danie de Jager (Danie.me)",
        "site_url": "https://danie.me/",
        "feed_url": "https://danie.me/feed.xml",
        "category": "Self-Hosting & HomeLab",
        "best_for": "Proxmox clustering, Ceph storage configs, and high-availability self-hosting.",
        "why_read": "Excellent technical devlogs on bare-metal virtualization, VLAN segmentation, and distributed storage.",
        "enabled": 1
    },
    {
        "id": "fediverse_report",
        "name": "Fediverse Report",
        "site_url": "https://fediversereport.com/",
        "feed_url": "https://fediversereport.com/feed/",
        "category": "Self-Hosting & HomeLab",
        "best_for": "ActivityPub protocols, decentralized social web developments, and node operations.",
        "why_read": "Independent publication tracking ActivityPub developments, Mastodon/Lemmy governance, and protocol standards.",
        "enabled": 1
    },
    {
        "id": "noted_lol",
        "name": "Noted.lol",
        "site_url": "https://noted.lol/",
        "feed_url": "https://noted.lol/rss/",
        "category": "Self-Hosting & HomeLab",
        "best_for": "Self-hosted software reviews, dashboard setups, and minimalist productivity tools.",
        "why_read": "Reviews of newly launched self-hosted web apps, showcasing UI design and Docker Compose deployments.",
        "enabled": 1
    }
]

CURATED_PRIVACY = [
    {
        "id": "schneier",
        "name": "Schneier on Security",
        "site_url": "https://www.schneier.com/",
        "feed_url": "https://www.schneier.com/feed/atom/",
        "category": "Privacy & Cryptography",
        "best_for": "Applied cryptography, security policy, and theoretical vulnerability analysis.",
        "why_read": "Bruce Schneier's blog remains essential for understanding security economics and cryptographic flaws.",
        "enabled": 1
    },
    {
        "id": "privacy_guides",
        "name": "Privacy Guides",
        "site_url": "https://www.privacyguides.org/",
        "feed_url": "https://discuss.privacyguides.net/posts.rss",
        "category": "Privacy & Cryptography",
        "best_for": "Audited privacy tools, threat-modeling frameworks, and hardened OS setups.",
        "why_read": "Non-profit guide operating with strict editorial independence and zero affiliate monetization.",
        "enabled": 1
    },
    {
        "id": "daniel_miessler",
        "name": "Daniel Miessler (Unsupervised Learning)",
        "site_url": "https://danielmiessler.com/",
        "feed_url": "https://danielmiessler.com/feed/",
        "category": "Privacy & Cryptography",
        "best_for": "Application security, threat modeling, and intersectional security/AI workflows.",
        "why_read": "Explores offensive security, vulnerability discovery techniques, and personal infrastructure hardening.",
        "enabled": 1
    },
    {
        "id": "trail_of_bits",
        "name": "Trail of Bits Blog",
        "site_url": "https://blog.trailofbits.com/",
        "feed_url": "https://blog.trailofbits.com/feed/",
        "category": "Privacy & Cryptography",
        "best_for": "Low-level software security, reverse engineering, binary exploitation, and compiler-level fixes.",
        "why_read": "Elite-tier vulnerability research and code-auditing engineering breaking down zero-days.",
        "enabled": 1
    },
    {
        "id": "troy_hunt",
        "name": "Troy Hunt (Have I Been Pwned)",
        "site_url": "https://www.troyhunt.com/",
        "feed_url": "https://www.troyhunt.com/rss/",
        "category": "Privacy & Cryptography",
        "best_for": "Data breach analysis, authentication pitfalls, and web API security.",
        "why_read": "Real-time postmortems on major breach datasets, credential stuffing, and web security architecture.",
        "enabled": 1
    },
    {
        "id": "portswigger",
        "name": "PortSwigger Research",
        "site_url": "https://portswigger.net/research",
        "feed_url": "https://portswigger.net/research/rss",
        "category": "Privacy & Cryptography",
        "best_for": "Cutting-edge HTTP desync attacks, SQLi, XSS, and modern web application exploitation.",
        "why_read": "The Burp Suite team produces original research into HTTP request smuggling and parser differentials.",
        "enabled": 1
    },
    {
        "id": "kuketz_security",
        "name": "Kuketz IT-Security Blog",
        "site_url": "https://www.kuketz-blog.de/",
        "feed_url": "https://www.kuketz-blog.de/feed/",
        "category": "Privacy & Cryptography",
        "best_for": "Android/iOS packet inspection, tracking telemetry removal, and mobile app micro-audits.",
        "why_read": "Network-level captures exposing covert tracking SDKs and insecure transmission in software.",
        "enabled": 1
    },
    {
        "id": "restore_privacy",
        "name": "RestorePrivacy",
        "site_url": "https://restoreprivacy.com/",
        "feed_url": "https://restoreprivacy.com/feed/",
        "category": "Privacy & Cryptography",
        "best_for": "Jurisdictional privacy laws, encrypted communication platforms, and browser fingerprinting.",
        "why_read": "Research on data retention mandates, cross-border surveillance pacts, and metadata isolation.",
        "enabled": 1
    },
    {
        "id": "crypto_engineering",
        "name": "Cryptographic Engineering (Matthew Green)",
        "site_url": "https://blog.cryptographyengineering.com/",
        "feed_url": "https://blog.cryptographyengineering.com/feed/",
        "category": "Privacy & Cryptography",
        "best_for": "Cryptographic protocol designs, zero-knowledge proofs, and end-to-end encryption mechanics.",
        "why_read": "Johns Hopkins cryptographer breaks down complex mathematical concepts and protocol flaws (Signal, TLS).",
        "enabled": 1
    },
    {
        "id": "graham_cluley",
        "name": "Graham Cluley",
        "site_url": "https://grahamcluley.com/",
        "feed_url": "https://grahamcluley.com/feed/",
        "category": "Privacy & Cryptography",
        "best_for": "Straightforward malware reporting, scam teardowns, and daily cyber hygiene news.",
        "why_read": "Veteran analyst providing quick, readable updates on active exploits and social engineering campaigns.",
        "enabled": 1
    }
]

CURATED_GAMEDEV = [
    {
        "id": "red_blob_games",
        "name": "Red Blob Games",
        "site_url": "https://www.redblobgames.com/",
        "feed_url": "https://www.redblobgames.com/blog/feed.xml",
        "category": "Game Dev & Engine Tech",
        "best_for": "Interactive 2D math, A* pathfinding, procedural tilemaps, and hexagonal grids.",
        "why_read": "Amit Patel's interactive, visual tutorials are the definitive resource for algorithmic gameplay math.",
        "enabled": 1
    },
    {
        "id": "inigo_quilez",
        "name": "Inigo Quilez",
        "site_url": "https://iquilezles.org/",
        "feed_url": "https://iquilezles.org/feed.xml",
        "category": "Game Dev & Engine Tech",
        "best_for": "Shader programming, raymarching, Signed Distance Functions (SDF), and procedural math.",
        "why_read": "Shadertoy co-creator offers masterclasses on rendering complex 3D worlds entirely through math formulas.",
        "enabled": 1
    },
    {
        "id": "fabien_sanglard",
        "name": "Fabien Sanglard",
        "site_url": "https://fabiensanglard.net/",
        "feed_url": "https://fabiensanglard.net/rss.xml",
        "category": "Game Dev & Engine Tech",
        "best_for": "Classic game engine code reviews (DOOM, Quake, Duke Nukem 3D, Another World).",
        "why_read": "Dissects architectures, assembly hacks, and memory constraints of legendary engines file by file.",
        "enabled": 1
    },
    {
        "id": "game_prog_patterns",
        "name": "Game Programming Patterns",
        "site_url": "https://gameprogrammingpatterns.com/",
        "feed_url": "https://journal.stuffwithstuff.com/rss.xml",
        "category": "Game Dev & Engine Tech",
        "best_for": "Architectural patterns, game loops, spatial partitioning, and component systems.",
        "why_read": "Indispensable guide on structuring clean, performant, and decoupled game code by Robert Nystrom.",
        "enabled": 1
    },
    {
        "id": "bit_101",
        "name": "Keith Peters (Bit-101)",
        "site_url": "https://www.bit-101.com/blog/",
        "feed_url": "https://www.bit-101.com/blog/feed/",
        "category": "Game Dev & Engine Tech",
        "best_for": "Procedural physics, generative art, and retro vector/canvas geometry.",
        "why_read": "Code experiments breaking down physics interactions, trigonometry, and canvas drawing.",
        "enabled": 1
    },
    {
        "id": "adrian_courreges",
        "name": "Adrian Courrèges",
        "site_url": "https://www.adriancourreges.com/",
        "feed_url": "https://www.adriancourreges.com/atom.xml",
        "category": "Game Dev & Engine Tech",
        "best_for": "Frame-by-frame graphics rendering studies (Doom 2016, GTA V, Deus Ex).",
        "why_read": "Dissects exactly how a single frame is drawn pass-by-pass (GBuffer, shadow maps, ambient occlusion).",
        "enabled": 1
    },
    {
        "id": "alan_zucconi",
        "name": "Alan Zucconi",
        "site_url": "https://www.alanzucconi.com/",
        "feed_url": "https://www.alanzucconi.com/feed/",
        "category": "Game Dev & Engine Tech",
        "best_for": "Volumetric lighting, shaders, non-Euclidean geometry, and physics simulations.",
        "why_read": "Deep technical math and rendering tutorials bridging theory and practical engine implementations.",
        "enabled": 1
    },
    {
        "id": "catlike_coding",
        "name": "Catlike Coding",
        "site_url": "https://catlikecoding.com/",
        "feed_url": "https://catlikecoding.com/feed.xml",
        "category": "Game Dev & Engine Tech",
        "best_for": "Procedural meshes, flow maps, custom SRP shaders, and hex maps.",
        "why_read": "Step-by-step guides providing the clearest explanations of modern graphics pipeline mechanics.",
        "enabled": 1
    },
    {
        "id": "game_engine_book",
        "name": "Game Engine Architecture",
        "site_url": "https://www.gameenginebook.com/",
        "feed_url": "https://www.gameenginebook.com/feed.xml",
        "category": "Game Dev & Engine Tech",
        "best_for": "Memory management, engine systems, animation pipelines, and profiling.",
        "why_read": "Companion insights and deep dives into real-world commercial engine design by Jason Gregory.",
        "enabled": 1
    },
    {
        "id": "simondev",
        "name": "SimonDev",
        "site_url": "https://simondev.teachable.com/",
        "feed_url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCEwhtpXrg5MmwlH04ANpL8A",
        "category": "Game Dev & Engine Tech",
        "best_for": "Procedural terrain generation, WebGL/Three.js engines, and quadtree spatial systems.",
        "why_read": "Focuses on building rendering systems, procedural planets, and physics from first principles.",
        "enabled": 1
    }
]

CURATED_LOCAL_AI = [
    {
        "id": "localllama",
        "name": "LocalLLaMA Community",
        "site_url": "https://www.reddit.com/r/LocalLLaMA/",
        "feed_url": "https://www.reddit.com/r/LocalLLaMA/.rss",
        "category": "Local AI & Machine Learning",
        "best_for": "Hardware benchmarking, quantization tests (GGUF, EXL2, AWQ), and fine-tuning setups.",
        "why_read": "Primary community driving consumer local LLM research with token-per-second benchmarks.",
        "enabled": 1
    },
    {
        "id": "huggingface_blog",
        "name": "Hugging Face Blog",
        "site_url": "https://huggingface.co/blog",
        "feed_url": "https://huggingface.co/blog/feed.xml",
        "category": "Local AI & Machine Learning",
        "best_for": "Open-source model releases, dataset curation, and parameter-efficient fine-tuning (PEFT/LoRA).",
        "why_read": "Technical heartbeat of open-weight ML with walkthroughs on training routines and transformer optimizations.",
        "enabled": 1
    },
    {
        "id": "the_gradient",
        "name": "The Gradient",
        "site_url": "https://thegradient.pub/",
        "feed_url": "https://thegradient.pub/rss/",
        "category": "Local AI & Machine Learning",
        "best_for": "Peer-written essays on ML architectures, scaling laws, and AI safety research.",
        "why_read": "Written by researchers and practitioners focusing on mathematical theory and implications of ML.",
        "enabled": 1
    },
    {
        "id": "sebastian_raschka",
        "name": "Ahead of AI (Sebastian Raschka)",
        "site_url": "https://magazine.sebastianraschka.com/",
        "feed_url": "https://magazine.sebastianraschka.com/feed",
        "category": "Local AI & Machine Learning",
        "best_for": "Building LLMs from scratch, PyTorch architectures, and fine-tuning mechanics.",
        "why_read": "Clear code-first explanations making complex transformer mechanics (flash attention, RoPE) accessible.",
        "enabled": 1
    },
    {
        "id": "interconnects",
        "name": "Interconnects (Nathan Lambert)",
        "site_url": "https://www.interconnects.ai/",
        "feed_url": "https://www.interconnects.ai/feed",
        "category": "Local AI & Machine Learning",
        "best_for": "Post-training, RLHF, DPO, and open-model governance.",
        "why_read": "Breaks down instruction tuning, preference optimization, and open-source model evaluations.",
        "enabled": 1
    },
    {
        "id": "simonwillison_ai",
        "name": "Simon Willison’s Weblog",
        "site_url": "https://simonwillison.net/",
        "feed_url": "https://simonwillison.net/atom/everything/",
        "category": "Local AI & Machine Learning",
        "best_for": "CLI tooling (LLM), local embeddings, prompt injection research, and SQLite integration.",
        "why_read": "Practical developer workflows for running small, fast models locally and building toolchains.",
        "enabled": 1
    },
    {
        "id": "tim_dettmers",
        "name": "Tim Dettmers' Blog",
        "site_url": "https://timdettmers.com/",
        "feed_url": "https://timdettmers.com/feed/",
        "category": "Local AI & Machine Learning",
        "best_for": "Consumer GPU hardware optimization, 4-bit quantization (QLoRA), and memory scaling.",
        "why_read": "Pioneer behind bitsandbytes and QLoRA; essential GPU buying guides and deep-memory analyses.",
        "enabled": 1
    },
    {
        "id": "ollama_releases",
        "name": "Ollama Engineering Releases",
        "site_url": "https://ollama.com/blog",
        "feed_url": "https://github.com/ollama/ollama/releases.atom",
        "category": "Local AI & Machine Learning",
        "best_for": "Local inference engine releases, Modelfile mechanics, and GPU backend optimizations.",
        "why_read": "Tracks cross-platform GPU layers optimization (ROCm, Metal, CUDA, Vulkan) for local models.",
        "enabled": 1
    },
    {
        "id": "latent_space",
        "name": "Latent Space (Swyx & Alessio)",
        "site_url": "https://www.latent.space/",
        "feed_url": "https://www.latent.space/feed",
        "category": "Local AI & Machine Learning",
        "best_for": "The AI engineer stack, local evals, inference frameworks (vLLM, SGLang), and system architectures.",
        "why_read": "Focuses on the engineering challenges of putting local and open models into production.",
        "enabled": 1
    },
    {
        "id": "lilian_weng",
        "name": "Lil'Log (Lilian Weng)",
        "site_url": "https://lilianweng.github.io/",
        "feed_url": "https://lilianweng.github.io/index.xml",
        "category": "Local AI & Machine Learning",
        "best_for": "Exhaustive, academic synthesis of ML papers (diffusion, attention, agents, reasoning).",
        "why_read": "Essential reference material summarizing complex research literature with mathematical precision.",
        "enabled": 1
    }
]

CURATED_HARDWARE = [
    {
        "id": "hackaday",
        "name": "Hackaday",
        "site_url": "https://hackaday.com/",
        "feed_url": "https://hackaday.com/feed/",
        "category": "Hardware & Electronics",
        "best_for": "Daily hardware hacks, circuit design, ESP32/RP2040 projects, and reverse engineering.",
        "why_read": "Gold standard daily publication for makers, firmware developers, and electrical engineers.",
        "enabled": 1
    },
    {
        "id": "adafruit",
        "name": "Adafruit Blog",
        "site_url": "https://learn.adafruit.com/",
        "feed_url": "https://blog.adafruit.com/feed/",
        "category": "Hardware & Electronics",
        "best_for": "MicroPython/CircuitPython, breakout boards, wearable electronics, and component guides.",
        "why_read": "Impeccably documented schematics, pinout guides, and code examples for physical computing.",
        "enabled": 1
    },
    {
        "id": "sparkfun",
        "name": "SparkFun News & Tutorials",
        "site_url": "https://www.sparkfun.com/news",
        "feed_url": "https://www.sparkfun.com/feeds/news",
        "category": "Hardware & Electronics",
        "best_for": "Sensor integration, wireless telemetry (LoRa, GNSS), and embedded prototyping.",
        "why_read": "Practical hardware interfacing, custom PCB development, and embedded programming.",
        "enabled": 1
    },
    {
        "id": "cnx_software",
        "name": "CNX Software",
        "site_url": "https://www.cnx-software.com/",
        "feed_url": "https://www.cnx-software.com/feed/",
        "category": "Hardware & Electronics",
        "best_for": "Single-board computers (SBCs), ARM/RISC-V development boards, and embedded Linux.",
        "why_read": "Exhaustive coverage and benchmarks of every new micro-computing board and SoC entering the market.",
        "enabled": 1
    },
    {
        "id": "dangerous_prototypes",
        "name": "Dangerous Prototypes",
        "site_url": "http://dangerousprototypes.com/",
        "feed_url": "http://dangerousprototypes.com/blog/feed/",
        "category": "Hardware & Electronics",
        "best_for": "Open-source hardware tools, bus pirates, logic analysis, and custom PCB prototyping.",
        "why_read": "Designing low-cost open hardware testing tools and reverse-engineering proprietary signals.",
        "enabled": 1
    },
    {
        "id": "greatscott",
        "name": "GreatScott! Labs",
        "site_url": "https://www.instructables.com/member/GreatScottLab/",
        "feed_url": "https://www.youtube.com/feeds/videos.xml?channel_id=UC6mIxFTvXkWQVE4P033YX6Q",
        "category": "Hardware & Electronics",
        "best_for": "Circuit design fundamentals, power electronics, buck converters, and battery safety.",
        "why_read": "Rigorous electronic testing comparing DIY circuits with oscilloscope readouts and efficiency data.",
        "enabled": 1
    },
    {
        "id": "bunnie_studios",
        "name": "Bunnie Studios (Andrew 'bunnie' Huang)",
        "site_url": "https://www.bunniestudios.com/",
        "feed_url": "https://www.bunniestudios.com/blog/feed/",
        "category": "Hardware & Electronics",
        "best_for": "Silicon reverse engineering, supply chain mechanics, and trusted hardware architecture.",
        "why_read": "Bunnie Huang offers unmatched insight into factory production, PCB assembly, and hardware security.",
        "enabled": 1
    },
    {
        "id": "low_level_learning",
        "name": "Low-Level Learning",
        "site_url": "https://lowlevel.eu/",
        "feed_url": "https://www.youtube.com/feeds/videos.xml?channel_id=UC6qj_mbvZwn2xOKodSD6dUg",
        "category": "Hardware & Electronics",
        "best_for": "Bare-metal C, assembly, memory registers, and microcontroller peripherals.",
        "why_read": "Breaks down how instructions interact with registers, interrupts, and memory on AVR and ARM chips.",
        "enabled": 1
    },
    {
        "id": "adrians_basement",
        "name": "Adrian's Digital Basement",
        "site_url": "https://adriansdigitalbasement.com/",
        "feed_url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCE5dIscvDxrbBoPPeyAgNWg",
        "category": "Hardware & Electronics",
        "best_for": "Component-level motherboard repair, CRT diagnostics, and vintage chip replacement.",
        "why_read": "Masterclasses in using logic probes and schematics to repair classic computing hardware.",
        "enabled": 1
    },
    {
        "id": "electromaker",
        "name": "Electromaker",
        "site_url": "https://www.electromaker.io/blog",
        "feed_url": "https://www.electromaker.io/blog/rss",
        "category": "Hardware & Electronics",
        "best_for": "Raspberry Pi, Arduino, and ESP32 project showcases and tutorials.",
        "why_read": "Great for discovering community physical computing builds, home automation sensors, and 3D enclosures.",
        "enabled": 1
    }
]

CURATED_MUSIC = [
    {
        "id": "bandcamp_daily",
        "name": "Bandcamp Daily",
        "site_url": "https://daily.bandcamp.com/",
        "feed_url": "https://daily.bandcamp.com/feed",
        "category": "Independent Music",
        "best_for": "Scene reports from around the world, underground releases, and artist-direct music.",
        "why_read": "High-caliber editorial work highlighting artists selling directly to listeners across global scenes.",
        "enabled": 1
    },
    {
        "id": "no_clean_singing",
        "name": "No Clean Singing",
        "site_url": "https://www.nocleansinging.com/",
        "feed_url": "https://www.nocleansinging.com/feed/",
        "category": "Independent Music",
        "best_for": "Extreme metal, death metal, grindcore, and black metal reviews.",
        "why_read": "Dedicated entirely to underground extreme music, spotlighting independent record labels.",
        "enabled": 1
    },
    {
        "id": "invisible_oranges",
        "name": "Invisible Oranges",
        "site_url": "https://www.invisibleoranges.com/",
        "feed_url": "https://www.invisibleoranges.com/feed/",
        "category": "Independent Music",
        "best_for": "Heavy metal history, philosophical critique, and underground previews.",
        "why_read": "Thoughtful, literary writing on metal subgenres, tracking emerging bands alongside classic retrospectives.",
        "enabled": 1
    },
    {
        "id": "maximumrocknroll",
        "name": "Maximum Rocknroll (MRR)",
        "site_url": "https://www.maximumrocknroll.com/",
        "feed_url": "https://www.maximumrocknroll.com/feed/",
        "category": "Independent Music",
        "best_for": "DIY punk, hardcore, garage rock zine culture, and underground scene reports.",
        "why_read": "The volunteer-run bible of DIY punk rock since 1977, reviewing hundreds of tapes, 7s, and demos.",
        "enabled": 1
    },
    {
        "id": "the_quietus",
        "name": "The Quietus",
        "site_url": "https://thequietus.com/",
        "feed_url": "https://thequietus.com/feed/",
        "category": "Independent Music",
        "best_for": "Avant-garde, industrial, post-punk, dark ambient, and left-field rock.",
        "why_read": "Independent UK-based journal prioritizing in-depth artist interviews and challenging music.",
        "enabled": 1
    },
    {
        "id": "stereogum",
        "name": "Stereogum (The Black Market)",
        "site_url": "https://www.stereogum.com/",
        "feed_url": "https://www.stereogum.com/feed/",
        "category": "Independent Music",
        "best_for": "Monthly underground metal curation and scene analysis.",
        "why_read": "Perceptive regular essays examining underground metal records, trends, and label movements.",
        "enabled": 1
    },
    {
        "id": "idioteq",
        "name": "IDIOTEQ",
        "site_url": "https://idioteq.com/",
        "feed_url": "https://idioteq.com/feed/",
        "category": "Independent Music",
        "best_for": "Hardcore, screamo, post-hardcore, and European DIY punk scenes.",
        "why_read": "Fiercely independent webzine providing long-form interviews with touring and underground bands.",
        "enabled": 1
    },
    {
        "id": "last_rites",
        "name": "Last Rites",
        "site_url": "https://yourlastrites.com/",
        "feed_url": "https://yourlastrites.com/feed/",
        "category": "Independent Music",
        "best_for": "Comprehensive heavy metal, progressive rock, and doom album reviews.",
        "why_read": "Track-by-track evaluations of heavy music releases without commercial PR bias.",
        "enabled": 1
    },
    {
        "id": "post_punk",
        "name": "Post-Punk.com",
        "site_url": "https://post-punk.com/",
        "feed_url": "https://post-punk.com/feed/",
        "category": "Independent Music",
        "best_for": "Goth, darkwave, synthpop, EBM, and industrial music.",
        "why_read": "Premier hub for modern dark alternative music, video premieres, and vintage reissues.",
        "enabled": 1
    },
    {
        "id": "treble",
        "name": "Treble",
        "site_url": "https://www.treblezine.com/",
        "feed_url": "https://www.treblezine.com/feed/",
        "category": "Independent Music",
        "best_for": "Album deep dives, genre starter guides, and alternative/experimental music rankings.",
        "why_read": "Context-rich writing spanning post-rock, alternative metal, hip-hop, and shoegaze.",
        "enabled": 1
    }
]

CURATED_FOOD = [
    {
        "id": "perfect_loaf",
        "name": "The Perfect Loaf (Maurizio Leo)",
        "site_url": "https://www.theperfectloaf.com/",
        "feed_url": "https://www.theperfectloaf.com/feed/",
        "category": "Food Science & Fermentation",
        "best_for": "Sourdough microbiology, baker's percentages, dough rheology, and hydration tables.",
        "why_read": "Scientific breakdowns of fermentation temperatures, levain building, and crumb structure.",
        "enabled": 1
    },
    {
        "id": "serious_eats",
        "name": "Serious Eats (The Food Lab)",
        "site_url": "https://www.seriouseats.com/",
        "feed_url": "https://www.seriouseats.com/rss",
        "category": "Food Science & Fermentation",
        "best_for": "Empirical culinary experiments, protein denaturing, Maillard reaction chemistry.",
        "why_read": "Tests culinary variables side-by-side using scientific methodology and cross-sectional photography.",
        "enabled": 1
    },
    {
        "id": "the_bread_code",
        "name": "The Bread Code",
        "site_url": "https://thebreadcode.com/",
        "feed_url": "https://thebreadcode.com/index.xml",
        "category": "Food Science & Fermentation",
        "best_for": "Open-source sourdough science, gluten matrix development, and flour analytics.",
        "why_read": "Engineering approach to sourdough baking, dissecting enzymes, ash content, and crust physics.",
        "enabled": 1
    },
    {
        "id": "cultures_for_health",
        "name": "Cultures for Health",
        "site_url": "https://www.culturesforhealth.com/learn/",
        "feed_url": "https://www.culturesforhealth.com/learn/feed/",
        "category": "Food Science & Fermentation",
        "best_for": "Wild fermentation, lacto-fermentation biology, koji cultivation, and misos.",
        "why_read": "Safety-first guides explaining pH curves, salinity percentages, and microbial succession.",
        "enabled": 1
    },
    {
        "id": "modernist_cuisine",
        "name": "Modernist Cuisine Blog",
        "site_url": "https://modernistcuisine.com/blog/",
        "feed_url": "https://modernistcuisine.com/feed/",
        "category": "Food Science & Fermentation",
        "best_for": "High-tech food science, sous-vide thermodynamics, hydrocolloids, and culinary physics.",
        "why_read": "Breaks down physical properties of food systems using lab equipment and centrifuges.",
        "enabled": 1
    },
    {
        "id": "king_arthur_flourish",
        "name": "King Arthur Baking: Flourish",
        "site_url": "https://www.kingarthurbaking.com/blog",
        "feed_url": "https://www.kingarthurbaking.com/blog/feed",
        "category": "Food Science & Fermentation",
        "best_for": "Flour protein profiles, starch gelatinization, autolyse timing, and baking chemistry.",
        "why_read": "Test kitchen deep-dives examining the specific science of ash content, enzyme activity, and hydration.",
        "enabled": 1
    },
    {
        "id": "revolution_fermentation",
        "name": "Revolution Fermentation",
        "site_url": "https://revolutionfermentation.com/",
        "feed_url": "https://revolutionfermentation.com/en/blogs/news.atom",
        "category": "Food Science & Fermentation",
        "best_for": "Kombucha, water kefir, tempeh, sourdough, and koji cultivation guides.",
        "why_read": "Variable-controlled fermentation protocols detailing exact brine percentages and incubation temperatures.",
        "enabled": 1
    },
    {
        "id": "amazing_ribs",
        "name": "AmazingRibs.com",
        "site_url": "https://amazingribs.com/",
        "feed_url": "https://amazingribs.com/feed/",
        "category": "Food Science & Fermentation",
        "best_for": "Meat thermodynamics, smoke chemistry, collagen breakdown, and brine diffusion.",
        "why_read": "Physicist Dr. Greg Blonder debunks barbecue myths by measuring heat transfer and salt penetration.",
        "enabled": 1
    },
    {
        "id": "puratos_sourdough",
        "name": "Puratos Sourdough Library",
        "site_url": "https://www.puratos.com/",
        "feed_url": "https://www.youtube.com/feeds/videos.xml?channel_id=UC6zS8QcR0R_4sWvR76Lkgsw",
        "category": "Food Science & Fermentation",
        "best_for": "Biodiversity of wild yeast strains, biodiversity cataloging, and fermentation kinetics.",
        "why_read": "Research into heritage sourdough strains and how ambient ecology alters bacterial composition.",
        "enabled": 1
    },
    {
        "id": "science_of_cooking",
        "name": "Science of Cooking",
        "site_url": "https://www.scienceofcooking.com/",
        "feed_url": "https://www.scienceofcooking.com/rss",
        "category": "Food Science & Fermentation",
        "best_for": "Molecular gastronomy, caramelization tables, enzyme functions, and culinary chemistry.",
        "why_read": "Reference-style resource detailing chemical compound transformations, melting points, and Maillard kinetics.",
        "enabled": 1
    }
]

# Combined Master Catalog: 110 Curated Publications across 11 Categories
CURATED_SOURCES_CATALOG = (
    CURATED_LINUX +
    CURATED_GAMING +
    CURATED_LABOR +
    CURATED_CULTURE +
    CURATED_SELFHOSTING +
    CURATED_PRIVACY +
    CURATED_GAMEDEV +
    CURATED_LOCAL_AI +
    CURATED_HARDWARE +
    CURATED_MUSIC +
    CURATED_FOOD
)
