## configuration de la couleur du shell
export LS_OPTIONS='--color=auto'
eval "$(dircolors)"
alias ls='ls $LS_OPTIONS'
alias ll='ls $LS_OPTIONS -la'
alias l='ls $LS_OPTIONS -lA'

## zone pour les alias
alias firew='bash /etc/init.d/firewall_Host.sh'
alias mynat='vim /etc/init.d/MyNatRules.config'

## configuration du repertoir de script
export PATH="$PATH:/etc/kora/script/"
for d in /etc/kora/script/*; do
  if [ -d "$d" ]; then
    PATH="$PATH:$d"
  fi
done

# Rendre exécutables tous les scripts .py et .sh
find /etc/kora/script/ -type f \( -name "*.py" -o -name "*.sh" \) -exec chmod +x {} \;

## commande pour le firewall et les regles nat
alias firew='bash /etc/init.d/kora_firewall.sh'
alias mynat='vim /etc/init.d/kora_nat_rules.config'

## Kobot pour l'allumage du shell
if [ -t 1 ]; then
        python3 /etc/kora/script/misc/kobot.py
fi
