<%*
// Prompt for the EOS path + description, then auto-generate the CERNBox link.
// Replaces the old copy-pasted "Path → Link Conversion" rules.
const path = await tp.system.prompt("EOS path (e.g. /eos/user/c/cgupta/public/...)");
const desc = await tp.system.prompt("Short description");
// CERNBox needs /eos/user/c/... not /eos/home-c/..., rooted at /files/spaces
const normalised = path.replace("/eos/home-c/cgupta", "/eos/user/c/cgupta");
const link = "https://cernbox.cern.ch/files/spaces" + normalised;
tR += "---\n";
tR += "tags: [plot]\n";
tR += "Date: " + tp.date.now("YYYY-MM-DD") + "\n";
tR += "Description: " + desc + "\n";
tR += "Link: " + link + "\n";
tR += "Path: " + path + "\n";
tR += "---\n";
tR += "\n# " + tp.file.title + "\n\n";
tR += "[🔗 Open in CERNBox](" + link + ")\n\n";
tR += "> EOS path: `" + path + "`\n";
-%>
