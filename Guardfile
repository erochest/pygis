
guard :shell do
  watch /index.md/ do |m|
    `pandoc -f markdown -t revealjs --smart --standalone --section-divs -o index.html -V theme:solarized --slide-level 2 index.md`
  end
end

